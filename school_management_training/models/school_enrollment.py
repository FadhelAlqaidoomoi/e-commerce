# -*- coding: utf-8 -*-
# =============================================================================
# ENROLLMENT MODEL
# =============================================================================
# This model handles student enrollments in courses.
# Complete all TODO items to implement the full functionality.
# =============================================================================

from datetime import date

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError


class SchoolEnrollment(models.Model):
    """
    Enrollment Model
    
    Manages the relationship between students and courses.
    
    Concepts covered:
    - Unique together constraint
    - Date validation
    - State workflow with validations
    - Automatic field computation
    - Record rules (security)
    """
    _name = 'school.enrollment'
    _description = 'Course Enrollment'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'enrollment_date desc'
    _rec_name = 'display_name'
    
    # ==========================================================================
    # TODO 1: Define Basic Fields
    # ==========================================================================
    # Add the following fields:
    # - enrollment_date: Date, required, default=today
    # - completion_date: Date (when student completes the course)
    # - notes: Text
    # - priority: Selection (0: Normal, 1: Low, 2: Medium, 3: High)
    # ==========================================================================
    
    # YOUR CODE HERE - Basic Fields
    
    
    # ==========================================================================
    # TODO 2: Define Relational Fields
    # ==========================================================================
    # Add the following fields:
    # - student_id: Many2one to 'school.student', required, ondelete='cascade'
    # - course_id: Many2one to 'school.course', required, ondelete='cascade'
    # - teacher_id: Many2one to 'school.teacher', related to course_id.teacher_id
    # ==========================================================================
    
    # YOUR CODE HERE - Relational Fields
    
    
    # ==========================================================================
    # TODO 3: Define State Field
    # ==========================================================================
    # Add state field with states:
    # - draft: Draft
    # - pending: Pending Approval
    # - confirmed: Confirmed
    # - completed: Completed
    # - cancelled: Cancelled
    # - dropped: Dropped
    # ==========================================================================
    
    # YOUR CODE HERE - State Field
    
    
    # ==========================================================================
    # TODO 4: Define Computed Fields
    # ==========================================================================
    # - display_name: Computed as "Student Name - Course Name"
    # - duration_days: Integer, days between enrollment_date and completion_date or today
    # - is_active: Boolean, True if state in ('confirmed', 'pending')
    # - student_grade: Float, related to the student's grade in this course
    # ==========================================================================
    
    display_name = fields.Char(
        string='Display Name',
        compute='_compute_display_name',
        store=True,
    )
    
    @api.depends('student_id', 'student_id.name', 'course_id', 'course_id.name')
    def _compute_display_name(self):
        """TODO: Implement display name computation"""
        for record in self:
            # YOUR CODE HERE
            record.display_name = ''
    
    # TODO: Implement remaining computed fields
    
    
    # ==========================================================================
    # TODO 5: Define Constraints
    # ==========================================================================
    # SQL Constraints:
    # - unique_student_course: A student can only enroll once per course
    #
    # Python Constraints:
    # - completion_date must be after enrollment_date
    # - Cannot enroll in a full course
    # - Cannot enroll if student doesn't meet prerequisites
    # ==========================================================================
    
    _sql_constraints = [
        ('unique_student_course', 'UNIQUE(student_id, course_id)', 
         'Student is already enrolled in this course!'),
        # TODO: Add more constraints if needed
    ]
    
    @api.constrains('enrollment_date', 'completion_date')
    def _check_dates(self):
        """TODO: Validate that completion_date is after enrollment_date"""
        for record in self:
            # YOUR CODE HERE
            pass
    
    # TODO: Implement remaining constraints
    
    
    # ==========================================================================
    # TODO 6: Implement Onchange Methods
    # ==========================================================================
    # - _onchange_course_id: Warn if course is almost full
    # - _onchange_student_id: Warn if student has low attendance rate
    # ==========================================================================
    
    # YOUR CODE HERE - Onchange methods
    
    
    # ==========================================================================
    # TODO 7: Implement State Transition Methods
    # ==========================================================================
    # - action_submit(): draft -> pending
    # - action_approve(): pending -> confirmed (check capacity)
    # - action_complete(): confirmed -> completed (set completion_date)
    # - action_cancel(): pending/confirmed -> cancelled
    # - action_drop(): confirmed -> dropped
    # - action_reset_draft(): cancelled/dropped -> draft
    # ==========================================================================
    
    def action_submit(self):
        """TODO: Submit enrollment for approval"""
        for record in self:
            # YOUR CODE HERE
            pass
    
    def action_approve(self):
        """TODO: Approve enrollment (check capacity)"""
        for record in self:
            # YOUR CODE HERE
            pass
    
    # TODO: Implement remaining action methods
    
    
    # ==========================================================================
    # TODO 8: Override CRUD Methods
    # ==========================================================================
    # - create(): Check prerequisites, check capacity, send notification
    # - write(): Track state changes
    # - unlink(): Cannot delete confirmed enrollments
    # ==========================================================================
    
    @api.model_create_multi
    def create(self, vals_list):
        """TODO: Implement create with validations"""
        # YOUR CODE HERE - Add validations before create
        return super().create(vals_list)
    
    # TODO: Implement write and unlink overrides
    
    
    # ==========================================================================
    # TODO 9: Implement Business Methods
    # ==========================================================================
    # - check_prerequisites(): Returns True if student meets course prerequisites
    # - calculate_final_grade(): Calculate and return final grade for enrollment
    # - send_confirmation_email(): Send confirmation email to student
    # - generate_certificate(): Generate completion certificate
    # ==========================================================================
    
    def check_prerequisites(self):
        """TODO: Check if student meets course prerequisites"""
        self.ensure_one()
        return True  # Implement actual logic
    
    # TODO: Implement remaining methods
