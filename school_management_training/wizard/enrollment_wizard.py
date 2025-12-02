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
    # TODO: Add remaining fields
    
    
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
        
        # YOUR CODE HERE
        # Check context for 'active_model' and 'active_ids'
        
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
        
        # YOUR CODE HERE
        
        # Return action to show created enrollments
        return {
            'type': 'ir.actions.act_window',
            'name': _('Created Enrollments'),
            'res_model': 'school.enrollment',
            'view_mode': 'list,form',
            'domain': [],  # Set domain to show created enrollments
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
        # YOUR CODE HERE
        return True
    
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
    # TODO: Add remaining fields
    
    
    # ==========================================================================
    # TODO 8: Implement Wizard Actions
    # ==========================================================================
    # - action_load_students(): Load enrolled students into line_ids
    # - action_save_grades(): Create grade records from line_ids
    # ==========================================================================
    
    def action_load_students(self):
        """TODO: Load enrolled students for grade entry"""
        self.ensure_one()
        # YOUR CODE HERE
        pass
    
    def action_save_grades(self):
        """TODO: Save all entered grades"""
        self.ensure_one()
        # YOUR CODE HERE
        pass


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
    # TODO: Add remaining fields


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
