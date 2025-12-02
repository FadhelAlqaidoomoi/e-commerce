# -*- coding: utf-8 -*-
# =============================================================================
# STUDENT MODEL
# =============================================================================
# This is the main student model for the school management system.
# Complete all TODO items to implement the full functionality.
# =============================================================================

from datetime import date
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError


class SchoolStudent(models.Model):
    """
    Student Model
    
    This model represents a student in the school system.
    Students can enroll in courses, receive grades, and have attendance tracked.
    
    Concepts covered:
    - Basic field types (Char, Text, Date, Selection, Boolean, Integer, Float)
    - Relational fields (Many2one, One2many, Many2many)
    - Computed fields with @api.depends
    - Constraints with @api.constrains
    - Onchange methods with @api.onchange
    - CRUD method overrides (create, write, unlink, copy)
    - Mail integration for messaging/chatter
    - Sequence generation
    - SQL constraints
    - State machine pattern
    """
    _name = 'school.student'
    _description = 'Student'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name asc'
    _rec_name = 'display_name'
    
    # ==========================================================================
    # TODO 1: Define Basic Fields
    # ==========================================================================
    # Add the following fields:
    # - student_code: Char field, readonly, copy=False (will be auto-generated)
    # - name: Char field, required, tracking=True
    # - last_name: Char field, required
    # - email: Char field with email validation
    # - phone: Char field
    # - date_of_birth: Date field, required
    # - gender: Selection field with options: male, female, other
    # - address: Text field
    # - photo: Binary field for student photo
    # - active: Boolean field with default True
    # - notes: Html field
    # ==========================================================================
    
    # YOUR CODE HERE - Basic Fields
    student_code = fields.Char(
        string='Student Code',
        readonly=True,
        copy=False,
        default=lambda self: _('New'),
    )
    # TODO: Add remaining basic fields below
    
    
    # ==========================================================================
    # TODO 2: Define Relational Fields
    # ==========================================================================
    # Add the following relational fields:
    # - guardian_id: Many2one to 'res.partner' (parent/guardian)
    # - enrollment_ids: One2many to 'school.enrollment' (inverse: student_id)
    # - course_ids: Many2many to 'school.course' (through school_student_course_rel)
    # - grade_ids: One2many to 'school.grade' (inverse: student_id)
    # - attendance_ids: One2many to 'school.attendance' (inverse: student_id)
    # - class_id: Many2one to 'school.course' for current primary class
    # ==========================================================================
    
    # YOUR CODE HERE - Relational Fields
    
    
    # ==========================================================================
    # TODO 3: Define Selection Field for State
    # ==========================================================================
    # Add a 'state' selection field with the following states:
    # - draft: Draft
    # - enrolled: Enrolled
    # - graduated: Graduated
    # - suspended: Suspended
    # - withdrawn: Withdrawn
    # Default should be 'draft', and it should have tracking=True
    # ==========================================================================
    
    # YOUR CODE HERE - State Field
    
    
    # ==========================================================================
    # TODO 4: Define Computed Fields
    # ==========================================================================
    # Implement the following computed fields:
    # 
    # 4.1 display_name: Combines name and last_name
    #     - Should compute as "last_name, name" (e.g., "Smith, John")
    #     - Depends on: name, last_name
    #
    # 4.2 age: Integer field computed from date_of_birth
    #     - Calculate years between date_of_birth and today
    #     - Depends on: date_of_birth
    #
    # 4.3 total_courses: Integer field counting enrolled courses
    #     - Count the number of records in enrollment_ids
    #     - Depends on: enrollment_ids
    #
    # 4.4 average_grade: Float field with digits=(5, 2)
    #     - Calculate average of all grades from grade_ids
    #     - Depends on: grade_ids.score
    #
    # 4.5 attendance_rate: Float field with digits=(5, 2)
    #     - Calculate percentage of 'present' attendance records
    #     - Depends on: attendance_ids.status
    # ==========================================================================
    
    # YOUR CODE HERE - Computed Fields
    display_name = fields.Char(
        string='Display Name',
        compute='_compute_display_name',
        store=True,
    )
    
    # TODO: Add age, total_courses, average_grade, attendance_rate fields
    # TODO: Implement all compute methods below
    
    @api.depends('name', 'last_name')
    def _compute_display_name(self):
        """
        TODO: Implement display_name computation
        Format: "last_name, name" (e.g., "Smith, John")
        Handle cases where last_name or name might be empty
        """
        for record in self:
            # YOUR CODE HERE
            pass
    
    # TODO: Implement _compute_age method
    
    # TODO: Implement _compute_total_courses method
    
    # TODO: Implement _compute_average_grade method
    
    # TODO: Implement _compute_attendance_rate method
    
    
    # ==========================================================================
    # TODO 5: Define SQL Constraints
    # ==========================================================================
    # Add _sql_constraints with:
    # - unique_student_code: student_code must be unique
    # - unique_email: email must be unique
    # - check_date_of_birth: date_of_birth must be in the past
    # ==========================================================================
    
    # YOUR CODE HERE - SQL Constraints
    _sql_constraints = [
        # ('unique_student_code', 'UNIQUE(student_code)', 'Student code must be unique!'),
        # TODO: Add more constraints
    ]
    
    
    # ==========================================================================
    # TODO 6: Define Python Constraints
    # ==========================================================================
    # Implement @api.constrains methods for:
    # 
    # 6.1 _check_age: Validate that student is between 5 and 100 years old
    #
    # 6.2 _check_email_format: Validate email contains @ symbol
    # ==========================================================================
    
    # YOUR CODE HERE - Python Constraints
    
    @api.constrains('date_of_birth')
    def _check_age(self):
        """
        TODO: Implement age validation
        - Student must be at least 5 years old
        - Student must be less than 100 years old
        - Raise ValidationError with appropriate message if invalid
        """
        for record in self:
            # YOUR CODE HERE
            pass
    
    # TODO: Implement _check_email_format method
    
    
    # ==========================================================================
    # TODO 7: Define Onchange Methods
    # ==========================================================================
    # Implement @api.onchange methods for:
    #
    # 7.1 _onchange_guardian: When guardian_id changes, if guardian has email,
    #     suggest to copy it to student's email (only if student email is empty)
    #
    # 7.2 _onchange_date_of_birth: Show a warning if student is under 6 years old
    # ==========================================================================
    
    # YOUR CODE HERE - Onchange Methods
    
    
    # ==========================================================================
    # TODO 8: Override CRUD Methods
    # ==========================================================================
    # 
    # 8.1 Override create():
    #     - Generate student_code using sequence 'school.student.sequence'
    #     - Post a message "Student record created" to chatter
    #
    # 8.2 Override write():
    #     - If state changes, post message about state change
    #     - Prevent editing if student is 'graduated' (raise UserError)
    #
    # 8.3 Override unlink():
    #     - Prevent deletion if student has any enrollments
    #     - Raise UserError with appropriate message
    #
    # 8.4 Override copy():
    #     - Clear student_code (should be regenerated)
    #     - Append " (Copy)" to the name
    #     - Reset state to 'draft'
    # ==========================================================================
    
    @api.model_create_multi
    def create(self, vals_list):
        """
        TODO: Implement create override
        - Generate sequence for student_code
        - Post creation message to chatter
        """
        for vals in vals_list:
            if vals.get('student_code', _('New')) == _('New'):
                vals['student_code'] = self.env['ir.sequence'].next_by_code('school.student.sequence') or _('New')
        
        records = super().create(vals_list)
        
        # TODO: Post message to chatter for each record
        
        return records
    
    # TODO: Implement write override
    
    # TODO: Implement unlink override
    
    # TODO: Implement copy override
    
    
    # ==========================================================================
    # TODO 9: Implement State Transition Methods (Action Buttons)
    # ==========================================================================
    # Implement button action methods for state transitions:
    #
    # 9.1 action_enroll(): draft -> enrolled
    #     - Validate student has at least one enrollment
    #
    # 9.2 action_graduate(): enrolled -> graduated
    #     - Validate average_grade >= 60
    #
    # 9.3 action_suspend(): enrolled -> suspended
    #     - Require a reason (use wizard or simple field)
    #
    # 9.4 action_withdraw(): any state -> withdrawn
    #
    # 9.5 action_reactivate(): suspended/withdrawn -> enrolled
    #     - Only allowed if student was previously enrolled
    #
    # 9.6 action_reset_to_draft(): any state -> draft
    #     - Only allowed for users with manager group
    # ==========================================================================
    
    def action_enroll(self):
        """
        TODO: Implement enrollment action
        - Change state from 'draft' to 'enrolled'
        - Validate that student has at least one enrollment
        - Post message about enrollment
        """
        for record in self:
            # YOUR CODE HERE
            pass
    
    # TODO: Implement remaining action methods
    
    
    # ==========================================================================
    # TODO 10: Implement Business Logic Methods
    # ==========================================================================
    # Implement the following business methods:
    #
    # 10.1 get_grade_summary(): Returns dict with grade statistics
    #      {'total': int, 'average': float, 'highest': float, 'lowest': float}
    #
    # 10.2 get_attendance_summary(): Returns attendance statistics dict
    #      {'total': int, 'present': int, 'absent': int, 'late': int, 'rate': float}
    #
    # 10.3 send_welcome_email(): Sends welcome email to student (use mail.template)
    #
    # 10.4 check_eligibility_for_graduation(): Returns True/False based on criteria
    #      - Average grade >= 60
    #      - Attendance rate >= 75
    #      - All required courses completed
    # ==========================================================================
    
    def get_grade_summary(self):
        """
        TODO: Implement grade summary calculation
        Return dict with: total, average, highest, lowest grades
        """
        self.ensure_one()
        # YOUR CODE HERE
        return {
            'total': 0,
            'average': 0.0,
            'highest': 0.0,
            'lowest': 0.0,
        }
    
    # TODO: Implement remaining business methods
    
    
    # ==========================================================================
    # TODO 11: Implement Search and Name Methods
    # ==========================================================================
    #
    # 11.1 Override _name_search to allow searching by:
    #      - student_code
    #      - name
    #      - last_name
    #      - email
    #
    # 11.2 Implement name_get alternative if needed (for special display)
    # ==========================================================================
    
    @api.model
    def _name_search(self, name='', domain=None, operator='ilike', limit=None, order=None):
        """
        TODO: Implement custom name search
        Allow searching by student_code, name, last_name, or email
        """
        domain = domain or []
        if name:
            domain = ['|', '|', '|',
                      ('student_code', operator, name),
                      ('name', operator, name),
                      ('last_name', operator, name),
                      ('email', operator, name)] + domain
        return self._search(domain, limit=limit, order=order)
