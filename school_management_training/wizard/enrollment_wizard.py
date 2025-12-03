# -*- coding: utf-8 -*-
# =============================================================================
# ENROLLMENT WIZARD
# =============================================================================
# This wizard handles bulk enrollment of students in courses.
# Complete all TODO items to implement the full functionality.
# =============================================================================

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError


class EnrollmentWizard(models.TransientModel):
    """
    Enrollment Wizard
    
    A transient model for bulk enrolling students in courses.
    
    Concepts covered:
    - TransientModel usage
    - Wizard workflow
    - Context handling
    - Multiple record processing
    - Return actions
    """
    _name = 'school.enrollment.wizard'
    _description = 'Bulk Enrollment Wizard'
    
    # ==========================================================================
    # TODO 1: Define Wizard Fields
    # ==========================================================================
    # Add the following fields:
    # - course_id: Many2one to 'school.course', required
    # - student_ids: Many2many to 'school.student'
    # - enrollment_date: Date, default=today
    # - send_notification: Boolean, default=True
    # - skip_prerequisites: Boolean, default=False
    # - notes: Text
    # ==========================================================================
    
    # YOUR CODE HERE - Wizard Fields
    course_id = fields.Many2one(
        comodel_name='school.course',
        string='Course',
        required=True,
    )
    student_ids = fields.Many2many('school.student', string='Students')
    enrollment_date = fields.Date(string='Enrollment Date', default=fields.Date.today)
    send_notification = fields.Boolean(string='Send Notification', default=True)
    skip_prerequisites = fields.Boolean(string='Skip Prerequisites Check', default=False)
    notes = fields.Text(string='Notes')
    
    
    # ==========================================================================
    # TODO 2: Define Default Methods
    # ==========================================================================
    # - _default_course_id: Get course from context if available
    # - _default_student_ids: Get students from context (active_ids)
    # ==========================================================================
    
    @api.model
    def default_get(self, fields_list):
        """
        TODO: Override default_get to set defaults from context
        - If called from a course, set course_id
        - If called from student list, set student_ids
        """
        res = super().default_get(fields_list)
        
        active_model = self.env.context.get('active_model')
        active_ids = self.env.context.get('active_ids', [])
        
        if active_model == 'school.course' and active_ids:
            res['course_id'] = active_ids[0]
        elif active_model == 'school.student' and active_ids:
            res['student_ids'] = [(6, 0, active_ids)]
        
        return res
    
    
    # ==========================================================================
    # TODO 3: Define Computed Fields
    # ==========================================================================
    # - available_seats: Integer, computed from course capacity
    # - student_count: Integer, count of selected students
    # - can_enroll_all: Boolean, True if all students can be enrolled
    # - warning_message: Text, computed warnings about capacity, prerequisites
    # ==========================================================================
    
    # YOUR CODE HERE - Computed fields
    
    
    # ==========================================================================
    # TODO 4: Implement Onchange Methods
    # ==========================================================================
    # - _onchange_course_id: Clear students that don't meet prerequisites
    # - _onchange_student_ids: Show warning if too many students selected
    # ==========================================================================
    
    # YOUR CODE HERE - Onchange methods
    
    
    # ==========================================================================
    # TODO 5: Implement Action Methods
    # ==========================================================================
    # - action_enroll(): Main action to create enrollments
    #   * Validate capacity
    #   * Check prerequisites (unless skip_prerequisites)
    #   * Create enrollment records
    #   * Send notifications if enabled
    #   * Return action to show created enrollments
    #
    # - action_enroll_and_new(): Enroll and open new wizard
    #
    # - action_cancel(): Close wizard
    # ==========================================================================
    
    def action_enroll(self):
        """
        TODO: Implement bulk enrollment action
        1. Validate inputs
        2. Check course capacity
        3. Check prerequisites for each student
        4. Create enrollment records
        5. Send notifications
        6. Return action to view created enrollments
        """
        self.ensure_one()
        
        if not self.student_ids:
            raise UserError('Please select at least one student!')
        
        if self.course_id.is_full and len(self.student_ids) > self.course_id.available_seats:
            raise UserError('Course does not have enough available seats!')
        
        created_enrollments = self.env['school.enrollment']
        
        for student in self.student_ids:
            # Check prerequisites
            if not self.skip_prerequisites and not self.course_id.check_prerequisites(student):
                raise UserError(f'Student {student.name} does not meet course prerequisites!')
            
            # Create enrollment
            enrollment = self.env['school.enrollment'].create({
                'student_id': student.id,
                'course_id': self.course_id.id,
                'enrollment_date': self.enrollment_date,
                'notes': self.notes,
                'state': 'draft',
            })
            created_enrollments += enrollment
        
        if self.send_notification:
            for enrollment in created_enrollments:
                enrollment.message_post(body='Bulk enrollment created')
        
        # Return action to show created enrollments
        return {
            'type': 'ir.actions.act_window',
            'name': _('Created Enrollments'),
            'res_model': 'school.enrollment',
            'view_mode': 'list,form',
            'domain': [('id', 'in', created_enrollments.ids)],
            'target': 'current',
        }
    
    def action_enroll_and_new(self):
        """TODO: Enroll students and open a new wizard"""
        self.action_enroll()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Bulk Enrollment'),
            'res_model': 'school.enrollment.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': self.env.context,
        }
    
    def action_cancel(self):
        """Close the wizard"""
        return {'type': 'ir.actions.act_window_close'}
    
    
    # ==========================================================================
    # TODO 6: Implement Helper Methods
    # ==========================================================================
    # - _check_prerequisites(student): Check if student meets prerequisites
    # - _get_eligible_students(): Filter students who can enroll
    # - _send_enrollment_notifications(enrollments): Send email notifications
    # ==========================================================================
    
    def _check_prerequisites(self, student):
        """TODO: Check if a student meets course prerequisites"""
        self.ensure_one()
        return self.course_id.check_prerequisites(student)
    
    # TODO: Implement remaining helper methods


class BulkGradeWizard(models.TransientModel):
    """
    Bulk Grade Entry Wizard
    
    Allows teachers to enter grades for multiple students at once.
    
    Concepts covered:
    - Wizard with line items
    - Dynamic form generation
    - One2many in transient models
    """
    _name = 'school.bulk.grade.wizard'
    _description = 'Bulk Grade Entry Wizard'
    
    # ==========================================================================
    # TODO 7: Define Bulk Grade Wizard Fields
    # ==========================================================================
    # - course_id: Many2one to 'school.course', required
    # - grade_date: Date, required, default=today
    # - grade_type: Selection (exam, quiz, assignment, etc.)
    # - max_score: Float, default=100
    # - description: Char
    # - line_ids: One2many to 'school.bulk.grade.wizard.line'
    # ==========================================================================
    
    course_id = fields.Many2one(
        comodel_name='school.course',
        string='Course',
        required=True,
    )
    grade_date = fields.Date(string='Grade Date', required=True, default=fields.Date.today)
    grade_type = fields.Selection([
        ('exam', 'Exam'),
        ('quiz', 'Quiz'),
        ('assignment', 'Assignment'),
        ('project', 'Project'),
        ('participation', 'Participation'),
        ('final', 'Final'),
    ], string='Grade Type')
    max_score = fields.Float(string='Max Score', default=100)
    description = fields.Char(string='Description')
    line_ids = fields.One2many('school.bulk.grade.wizard.line', 'wizard_id', string='Grade Lines')
    
    
    # ==========================================================================
    # TODO 8: Implement Wizard Actions
    # ==========================================================================
    # - action_load_students(): Load enrolled students into line_ids
    # - action_save_grades(): Create grade records from line_ids
    # ==========================================================================
    
    def action_load_students(self):
        """TODO: Load enrolled students for grade entry"""
        self.ensure_one()
        enrollments = self.env['school.enrollment'].search([
            ('course_id', '=', self.course_id.id),
            ('state', '=', 'confirmed'),
        ])
        
        lines = []
        for enrollment in enrollments:
            lines.append((0, 0, {
                'student_id': enrollment.student_id.id,
            }))
        
        self.line_ids = lines
    
    def action_save_grades(self):
        """TODO: Save all entered grades"""
        self.ensure_one()
        for line in self.line_ids:
            if line.score is not None:
                self.env['school.grade'].create({
                    'student_id': line.student_id.id,
                    'course_id': self.course_id.id,
                    'score': line.score,
                    'max_score': self.max_score,
                    'grade_type': self.grade_type,
                    'description': self.description,
                    'feedback': line.feedback,
                    'date': self.grade_date,
                })
        
        return {'type': 'ir.actions.act_window_close'}


class BulkGradeWizardLine(models.TransientModel):
    """Line items for bulk grade entry"""
    _name = 'school.bulk.grade.wizard.line'
    _description = 'Bulk Grade Entry Line'
    
    # ==========================================================================
    # TODO 9: Define Line Fields
    # ==========================================================================
    # - wizard_id: Many2one to 'school.bulk.grade.wizard'
    # - student_id: Many2one to 'school.student', required
    # - score: Float
    # - feedback: Text
    # ==========================================================================
    
    wizard_id = fields.Many2one(
        comodel_name='school.bulk.grade.wizard',
        string='Wizard',
        required=True,
        ondelete='cascade',
    )
    student_id = fields.Many2one('school.student', string='Student', required=True)
    score = fields.Float(string='Score')
    feedback = fields.Text(string='Feedback')


class BulkAttendanceWizard(models.TransientModel):
    """
    Bulk Attendance Wizard
    
    Allows marking attendance for multiple students at once.
    """
    _name = 'school.bulk.attendance.wizard'
    _description = 'Bulk Attendance Wizard'
    
    # ==========================================================================
    # TODO 10: Define Bulk Attendance Wizard
    # ==========================================================================
    # Similar structure to BulkGradeWizard:
    # - course_id: Many2one to 'school.course'
    # - attendance_date: Date
    # - line_ids: One2many to 'school.bulk.attendance.wizard.line'
    # - action_mark_all_present(): Mark all students present
    # - action_save(): Save attendance records
    # ==========================================================================
    
    course_id = fields.Many2one(
        comodel_name='school.course',
        string='Course',
        required=True,
    )
    attendance_date = fields.Date(
        string='Date',
        required=True,
        default=fields.Date.today,
    )
    # TODO: Complete the wizard implementation


class BulkAttendanceWizardLine(models.TransientModel):
    """Line items for bulk attendance"""
    _name = 'school.bulk.attendance.wizard.line'
    _description = 'Bulk Attendance Line'
    
    wizard_id = fields.Many2one(
        comodel_name='school.bulk.attendance.wizard',
        string='Wizard',
        required=True,
        ondelete='cascade',
    )
    # TODO: Add student_id, status, check_in, remarks fields
