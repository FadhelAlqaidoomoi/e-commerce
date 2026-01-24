# -*- coding: utf-8 -*-
# Part of Fadhel Addons. See LICENSE file for full copyright and licensing details.

import uuid
import logging
from datetime import timedelta

from odoo import api, fields, models

_logger = logging.getLogger(__name__)

# Token expiry duration
TOKEN_EXPIRY_DAYS = 30


class EcommerceCartToken(models.Model):
    """
    Cart token model for persistent guest cart management.
    Allows guests to recover their cart even after session expires.
    """
    _name = 'ecommerce.cart.token'
    _description = 'Guest Cart Token'
    _order = 'create_date desc'

    token = fields.Char(
        string='Token',
        required=True,
        index=True,
        readonly=True,
        copy=False,
        default=lambda self: str(uuid.uuid4())
    )

    sale_order_id = fields.Many2one(
        'sale.order',
        string='Sale Order',
        required=True,
        ondelete='cascade',
        index=True
    )

    guest_email = fields.Char(
        string='Guest Email',
        index=True,
        help='Email provided during guest checkout (for order linking)'
    )

    guest_phone = fields.Char(
        string='Guest Phone',
        help='Phone provided during guest checkout'
    )

    is_claimed = fields.Boolean(
        string='Claimed',
        default=False,
        help='Token has been claimed by a registered user'
    )

    claimed_by_partner_id = fields.Many2one(
        'res.partner',
        string='Claimed By',
        ondelete='set null'
    )

    claimed_date = fields.Datetime(
        string='Claimed Date'
    )

    expires_at = fields.Datetime(
        string='Expires At',
        required=True,
        default=lambda self: fields.Datetime.now() + timedelta(days=TOKEN_EXPIRY_DAYS)
    )

    last_activity = fields.Datetime(
        string='Last Activity',
        default=fields.Datetime.now
    )

    _sql_constraints = [
        ('token_unique', 'UNIQUE(token)', 'Cart token must be unique'),
    ]

    @api.model
    def generate_token(self, sale_order_id, guest_email=None, guest_phone=None):
        """
        Generate a new cart token for a sale order.

        Args:
            sale_order_id: ID of the sale.order
            guest_email: Optional guest email for future linking
            guest_phone: Optional guest phone for future linking

        Returns:
            ecommerce.cart.token record
        """
        return self.create({
            'sale_order_id': sale_order_id,
            'guest_email': guest_email,
            'guest_phone': guest_phone,
        })

    def validate_token(self):
        """
        Validate that the token is still usable.

        Returns:
            tuple: (is_valid: bool, error_code: str or None, error_message: str or None)
        """
        self.ensure_one()

        # Check if claimed
        if self.is_claimed:
            return False, 'TOKEN_CLAIMED', 'This cart has been claimed by another account'

        # Check expiry
        if self.expires_at < fields.Datetime.now():
            return False, 'TOKEN_EXPIRED', 'Cart token has expired'

        # Check order exists
        if not self.sale_order_id.exists():
            return False, 'ORDER_NOT_FOUND', 'Associated cart not found'

        # Check order is still draft
        if self.sale_order_id.state != 'draft':
            return False, 'ORDER_NOT_DRAFT', 'Cart has already been checked out'

        return True, None, None

    def claim_token(self, partner):
        """
        Mark token as claimed by a registered user.

        Args:
            partner: res.partner record claiming the token
        """
        self.ensure_one()
        self.write({
            'is_claimed': True,
            'claimed_by_partner_id': partner.id,
            'claimed_date': fields.Datetime.now(),
        })
        _logger.info(
            'Cart token %s claimed by partner %s (ID: %s)',
            self.token[:8], partner.name, partner.id
        )

    def refresh_expiry(self):
        """
        Extend token expiry on activity.
        Called when cart is accessed or modified.
        """
        self.write({
            'expires_at': fields.Datetime.now() + timedelta(days=TOKEN_EXPIRY_DAYS),
            'last_activity': fields.Datetime.now(),
        })

    def update_guest_info(self, email=None, phone=None):
        """
        Update guest contact information on the token.

        Args:
            email: Guest email address
            phone: Guest phone number
        """
        vals = {}
        if email:
            vals['guest_email'] = email
        if phone:
            vals['guest_phone'] = phone
        if vals:
            self.write(vals)

    @api.model
    def _cron_cleanup_expired_tokens(self):
        """
        Scheduled job to clean up expired tokens.
        Run daily via Odoo cron.
        """
        # Find expired unclaimed tokens
        expired = self.search([
            ('expires_at', '<', fields.Datetime.now()),
            ('is_claimed', '=', False),
        ])

        count = len(expired)
        if count > 0:
            # For tokens with very old draft orders, archive the orders
            cutoff = fields.Datetime.now() - timedelta(days=45)
            for token in expired:
                if (token.sale_order_id.exists() and
                    token.sale_order_id.state == 'draft' and
                    token.last_activity and
                    token.last_activity < cutoff):
                    # Archive old abandoned cart
                    token.sale_order_id.write({'active': False})

            expired.unlink()
            _logger.info('Cleaned up %d expired cart tokens', count)

    @api.model
    def find_by_token(self, token_str):
        """
        Find a token record by its token string.

        Args:
            token_str: The UUID token string

        Returns:
            ecommerce.cart.token record or empty recordset
        """
        if not token_str:
            return self.browse()
        return self.search([('token', '=', token_str)], limit=1)

    @api.model
    def get_valid_token_for_order(self, order_id):
        """
        Get a valid (unclaimed, unexpired) token for an order.

        Args:
            order_id: ID of the sale.order

        Returns:
            ecommerce.cart.token record or empty recordset
        """
        return self.search([
            ('sale_order_id', '=', order_id),
            ('is_claimed', '=', False),
            ('expires_at', '>', fields.Datetime.now()),
        ], limit=1)
