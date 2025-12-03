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
    enrollment_date = fields.Date(string='Enrollment Date', required=True, default=fields.Date.today)
    completion_date = fields.Date(string='Completion Date')
    notes = fields.Text(string='Notes')
    priority = fields.Selection([
        ('0', 'Normal'),
        ('1', 'Low'),
        ('2', 'Medium'),
        ('3', 'High'),
    ], string='Priority', default='0')
    
    
    # ==========================================================================
    # TODO 2: Define Relational Fields
    # ==========================================================================
    # Add the following fields:
    # - student_id: Many2one to 'school.student', required, ondelete='cascade'
    # - course_id: Many2one to 'school.course', required, ondelete='cascade'
    # - teacher_id: Many2one to 'school.teacher', related to course_id.teacher_id
    # ==========================================================================
    
    # YOUR CODE HERE - Relational Fields
    student_id = fields.Many2one('school.student', string='Student', required=True, ondelete='cascade')
    course_id = fields.Many2one('school.course', string='Course', required=True, ondelete='cascade')
    teacher_id = fields.Many2one('school.teacher', string='Teacher', related='course_id.teacher_id', readonly=True)
    
    
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
    state = fields.Selection([
        ('draft', 'Draft'),
        ('pending', 'Pending Approval'),
        ('confirmed', 'Confirmed'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('dropped', 'Dropped'),
    ], string='State', default='draft', tracking=True)
    
    
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
    duration_days = fields.Integer(string='Duration Days', compute='_compute_duration_days', store=True)
    is_active = fields.Boolean(string='Is Active', compute='_compute_is_active', store=True)
    student_grade = fields.Float(string='Student Grade', compute='_compute_student_grade', digits=(5, 2), store=True)
    
    @api.depends('student_id', 'student_id.name', 'course_id', 'course_id.name')
    def _compute_display_name(self):
        """TODO: Implement display name computation"""
        for record in self:
            record.display_name = f"{record.student_id.name} - {record.course_id.name}"
    
    @api.depends('enrollment_date', 'completion_date')
    def _compute_duration_days(self):
        """Compute duration in days"""
        for record in self:
            if record.completion_date:
                record.duration_days = (record.completion_date - record.enrollment_date).days
            else:
                record.duration_days = (date.today() - record.enrollment_date).days
    
    @api.depends('state')
    def _compute_is_active(self):
        """Check if enrollment is active"""
        for record in self:
            record.is_active = record.state in ('confirmed', 'pending')
    
    @api.depends('student_id', 'course_id')
    def _compute_student_grade(self):
        """Get student's grade in this course"""
        for record in self:
            grades = record.student_id.grade_ids.filtered(lambda g: g.course_id.id == record.course_id.id)
            if grades:
                percentages = [(g.score / g.max_score * 100) if g.max_score > 0 else 0 for g in grades]
                record.student_grade = sum(percentages) / len(percentages) if percentages else 0.0
            else:
                record.student_grade = 0.0
    
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
            if record.completion_date and record.completion_date < record.enrollment_date:
                raise ValidationError('Completion date must be after enrollment date!')
    
    @api.constrains('course_id')
    def _check_course_capacity(self):
        """Check course is not full"""
        for record in self:
            if record.course_id.is_full and record.state in ('draft', 'pending'):
                raise ValidationError('Course is full! Cannot enroll more students.')
    
    # TODO: Implement remaining constraints
    
    
    # ==========================================================================
    # TODO 6: Implement Onchange Methods
    # ==========================================================================
    # - _onchange_course_id: Warn if course is almost full
    # - _onchange_student_id: Warn if student has low attendance rate
    # ==========================================================================
    
    @api.onchange('course_id')
    def _onchange_course_id(self):
        """Warn if course is almost full"""
        if self.course_id and self.course_id.available_seats <= 2:
            return {'warning': {'title': 'Warning', 'message': 'Course is almost full!'}}
    
    @api.onchange('student_id')
    def _onchange_student_id(self):
        """Warn if student has low attendance"""
        if self.student_id and self.student_id.attendance_rate < 75:
            return {'warning': {'title': 'Warning', 'message': f"Student's attendance rate is {self.student_id.attendance_rate}%"}}
    
    
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
        """Submit enrollment for approval"""
        for record in self:
            record.state = 'pending'
            record.message_post(body='Enrollment submitted for approval')
    
    def action_approve(self):
        """Approve enrollment (check capacity)"""
        for record in self:
            if record.course_id.is_full:
                raise UserError('Cannot approve: Course is full!')
            record.state = 'confirmed'
            record.message_post(body='Enrollment approved and confirmed')
    
    def action_complete(self):
        """Complete the enrollment"""
        for record in self:
            record.state = 'completed'
            record.completion_date = date.today()
            record.message_post(body='Enrollment completed')
    
    def action_cancel(self):
        """Cancel the enrollment"""
        for record in self:
            record.state = 'cancelled'
            record.message_post(body='Enrollment cancelled')
    
    def action_drop(self):
        """Drop the course"""
        for record in self:
            record.state = 'dropped'
            record.message_post(body='Student dropped the course')
    
    def action_reset_draft(self):
        """Reset to draft"""
        for record in self:
            if record.state not in ('cancelled', 'dropped'):
                raise UserError('Only cancelled or dropped enrollments can be reset!')
            record.state = 'draft'
            record.message_post(body='Enrollment reset to draft')
    
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
        """Implement create with validations"""
        for vals in vals_list:
            if 'student_id' in vals and 'course_id' in vals:
                student = self.env['school.student'].browse(vals['student_id'])
                course = self.env['school.course'].browse(vals['course_id'])
                # Check prerequisites
                if not course.check_prerequisites(student):
                    raise UserError('Student does not meet course prerequisites!')
        return super().create(vals_list)
    
    def write(self, vals):
        """Track state changes"""
        result = super().write(vals)
        if 'state' in vals:
            for record in self:
                state_label = dict(record._fields['state'].selection).get(vals['state'], vals['state'])
                record.message_post(body=f'State changed to: {state_label}')
        return result
    
    def unlink(self):
        """Cannot delete confirmed enrollments"""
        for record in self:
            if record.state == 'confirmed':
                raise UserError('Cannot delete confirmed enrollments!')
        return super().unlink()
    
    
    # ==========================================================================
    # TODO 9: Implement Business Methods
    # ==========================================================================
    # - check_prerequisites(): Returns True if student meets course prerequisites
    # - calculate_final_grade(): Calculate and return final grade for enrollment
    # - send_confirmation_email(): Send confirmation email to student
    # - generate_certificate(): Generate completion certificate
    # ==========================================================================
    
    def check_prerequisites(self):
        """Check if student meets course prerequisites"""
        self.ensure_one()
        return self.course_id.check_prerequisites(self.student_id)
    
    def calculate_final_grade(self):
        """Calculate and return final grade for enrollment"""
        self.ensure_one()
        if not self.student_id.grade_ids.filtered(lambda g: g.course_id.id == self.course_id.id):
            return 0.0
        return self.student_grade
    
    # TODO: Implement remaining methods
