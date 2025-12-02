# -*- coding: utf-8 -*-
# =============================================================================
# TEACHER MODEL
# =============================================================================
# This model represents teachers in the school system.
# Complete all TODO items to implement the full functionality.
# =============================================================================

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError


class SchoolTeacher(models.Model):
    """
    Teacher Model
    
    Concepts covered:
    - Delegation inheritance (_inherits)
    - Related fields
    - Default values with lambda
    - Domain filters on relational fields
    - Monetary fields
    - Company-dependent fields
    """
    _name = 'school.teacher'
    _description = 'Teacher'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name asc'
    
    # ==========================================================================
    # TODO 1: Define Basic Fields
    # ==========================================================================
    # Add the following fields:
    # - employee_code: Char field, readonly, copy=False (auto-generated)
    # - name: Char field, required, tracking=True
    # - email: Char field, required
    # - phone: Char field
    # - date_of_birth: Date field
    # - hire_date: Date field, required, default=today
    # - department: Selection (science, arts, mathematics, languages, physical_education, other)
    # - qualification: Char field
    # - experience_years: Integer field with default 0
    # - biography: Html field
    # - photo: Binary field
    # - active: Boolean with default True
    # ==========================================================================
    
    # YOUR CODE HERE - Basic Fields
    employee_code = fields.Char(
        string='Employee Code',
        readonly=True,
        copy=False,
        default=lambda self: _('New'),
    )
    # TODO: Add remaining basic fields
    
    
    # ==========================================================================
    # TODO 2: Define Monetary Field
    # ==========================================================================
    # Add salary field:
    # - salary: Monetary field
    # - currency_id: Many2one to 'res.currency' (use company's currency as default)
    # 
    # Hint: For monetary fields, you need both the monetary field and a currency field
    # ==========================================================================
    
    # YOUR CODE HERE - Monetary Fields
    
    
    # ==========================================================================
    # TODO 3: Define Relational Fields
    # ==========================================================================
    # Add the following relational fields:
    # - course_ids: One2many to 'school.course' (inverse: teacher_id)
    # - user_id: Many2one to 'res.users' (linked portal user)
    # - company_id: Many2one to 'res.company' with default
    # ==========================================================================
    
    # YOUR CODE HERE - Relational Fields
    
    
    # ==========================================================================
    # TODO 4: Define Computed Fields
    # ==========================================================================
    # Implement:
    # - total_courses: Integer, count of course_ids
    # - total_students: Integer, count of all students across all courses
    # - age: Integer, calculated from date_of_birth
    # - years_of_service: Integer, calculated from hire_date
    # ==========================================================================
    
    # YOUR CODE HERE - Computed Fields and their compute methods
    
    
    # ==========================================================================
    # TODO 5: Define Related Fields
    # ==========================================================================
    # Add related fields:
    # - company_name: Char, related to company_id.name
    # - company_currency_id: Many2one, related to company_id.currency_id
    # ==========================================================================
    
    # YOUR CODE HERE - Related Fields
    
    
    # ==========================================================================
    # TODO 6: Define SQL and Python Constraints
    # ==========================================================================
    # SQL Constraints:
    # - unique_employee_code: employee_code must be unique
    # - check_experience: experience_years must be >= 0
    #
    # Python Constraints:
    # - hire_date cannot be in the future
    # - salary must be positive if provided
    # ==========================================================================
    
    _sql_constraints = [
        # YOUR CODE HERE
    ]
    
    # YOUR CODE HERE - Python constraints
    
    
    # ==========================================================================
    # TODO 7: Override create method
    # ==========================================================================
    # - Generate employee_code using sequence 'school.teacher.sequence'
    # - Post creation message
    # ==========================================================================
    
    @api.model_create_multi
    def create(self, vals_list):
        """TODO: Implement create override"""
        for vals in vals_list:
            if vals.get('employee_code', _('New')) == _('New'):
                vals['employee_code'] = self.env['ir.sequence'].next_by_code('school.teacher.sequence') or _('New')
        return super().create(vals_list)
    
    
    # ==========================================================================
    # TODO 8: Implement Business Methods
    # ==========================================================================
    # 
    # 8.1 get_courses_summary(): Returns dict with course statistics
    #
    # 8.2 assign_to_course(course_id): Assigns teacher to a course
    #     - Validate teacher is not already assigned
    #     - Update course's teacher_id
    #
    # 8.3 remove_from_course(course_id): Removes teacher from a course
    # ==========================================================================
    
    def get_courses_summary(self):
        """TODO: Implement course summary"""
        self.ensure_one()
        return {
            'total_courses': 0,
            'total_students': 0,
            'courses': [],
        }
    
    # TODO: Implement remaining methods
