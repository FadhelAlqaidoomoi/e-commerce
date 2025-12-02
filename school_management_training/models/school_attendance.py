# -*- coding: utf-8 -*-
# =============================================================================
# ATTENDANCE MODEL
# =============================================================================
# This model handles student attendance tracking.
# Complete all TODO items to implement the full functionality.
# =============================================================================

from datetime import date, datetime, timedelta

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError


class SchoolAttendance(models.Model):
    """
    Attendance Model
    
    Tracks daily attendance for students in courses.
    
    Concepts covered:
    - Datetime fields
    - Unique constraint with multiple fields
    - Batch operations
    - Scheduled actions (cron)
    """
    _name = 'school.attendance'
    _description = 'Student Attendance'
    _order = 'date desc, check_in desc'
    _rec_name = 'display_name'
    
    # ==========================================================================
    # TODO 1: Define Basic Fields
    # ==========================================================================
    # Add the following fields:
    # - date: Date, required, default=today, index=True
    # - check_in: Datetime (when student checked in)
    # - check_out: Datetime (when student checked out)
    # - status: Selection (present, absent, late, excused, half_day)
    # - remarks: Text (reason for absence, etc.)
    # - is_excused: Boolean (whether absence is excused)
    # ==========================================================================
    
    # YOUR CODE HERE - Basic Fields
    date = fields.Date(
        string='Date',
        required=True,
        default=fields.Date.today,
        index=True,
    )
    # TODO: Add remaining basic fields
    
    
    # ==========================================================================
    # TODO 2: Define Relational Fields
    # ==========================================================================
    # - student_id: Many2one to 'school.student', required, ondelete='cascade'
    # - course_id: Many2one to 'school.course', required, ondelete='cascade'
    # - recorded_by: Many2one to 'res.users', default=current user
    # ==========================================================================
    
    # YOUR CODE HERE - Relational Fields
    
    
    # ==========================================================================
    # TODO 3: Define Computed Fields
    # ==========================================================================
    # - display_name: "Student - Course - Date (Status)"
    # - duration_hours: Float, computed from check_in and check_out
    # - is_on_time: Boolean, True if check_in before 9:00 AM
    # - day_of_week: Selection, computed from date (monday, tuesday, etc.)
    # ==========================================================================
    
    display_name = fields.Char(
        string='Display Name',
        compute='_compute_display_name',
        store=True,
    )
    
    @api.depends('student_id', 'course_id', 'date', 'status')
    def _compute_display_name(self):
        """TODO: Implement display name"""
        for record in self:
            # YOUR CODE HERE
            record.display_name = ''
    
    # TODO: Implement remaining computed fields
    
    
    # ==========================================================================
    # TODO 4: Define Constraints
    # ==========================================================================
    # SQL Constraints:
    # - unique_attendance: One record per student per course per date
    #
    # Python Constraints:
    # - check_out must be after check_in
    # - date cannot be in the future
    # - Student must be enrolled in the course
    # ==========================================================================
    
    _sql_constraints = [
        ('unique_attendance', 'UNIQUE(student_id, course_id, date)', 
         'Attendance already recorded for this student in this course on this date!'),
    ]
    
    @api.constrains('check_in', 'check_out')
    def _check_times(self):
        """TODO: Validate check_out is after check_in"""
        for record in self:
            # YOUR CODE HERE
            pass
    
    # TODO: Implement remaining constraints
    
    
    # ==========================================================================
    # TODO 5: Implement Onchange Methods
    # ==========================================================================
    # - _onchange_check_in: If check_in is after 9:00, suggest status='late'
    # - _onchange_status: If status is 'excused', set is_excused=True
    # ==========================================================================
    
    # YOUR CODE HERE - Onchange methods
    
    
    # ==========================================================================
    # TODO 6: Implement Business Methods
    # ==========================================================================
    # - mark_present(): Quick action to mark as present with current time
    # - mark_absent(): Quick action to mark as absent
    # - get_student_attendance_summary(student_id, date_from, date_to):
    #   Returns attendance statistics for a student in date range
    # ==========================================================================
    
    def mark_present(self):
        """TODO: Mark attendance as present with current time"""
        # YOUR CODE HERE
        pass
    
    def mark_absent(self):
        """TODO: Mark attendance as absent"""
        # YOUR CODE HERE
        pass
    
    # TODO: Implement remaining methods
    
    
    # ==========================================================================
    # TODO 7: Implement Batch/Bulk Operations
    # ==========================================================================
    # - bulk_create_attendance(course_id, date): Creates attendance records
    #   for all enrolled students in a course for a given date
    # - bulk_mark_present(ids): Marks multiple records as present
    # - bulk_mark_absent(ids): Marks multiple records as absent
    # ==========================================================================
    
    @api.model
    def bulk_create_attendance(self, course_id, attendance_date=None):
        """
        TODO: Create attendance records for all enrolled students
        Creates 'absent' records by default that can be updated to 'present'
        """
        if attendance_date is None:
            attendance_date = fields.Date.today()
        
        # YOUR CODE HERE
        # 1. Get course and its confirmed enrollments
        # 2. For each enrolled student, create attendance record if not exists
        # 3. Return created records
        
        return self.env['school.attendance']
    
    # TODO: Implement bulk_mark_present and bulk_mark_absent
    
    
    # ==========================================================================
    # TODO 8: Implement Scheduled Action Method
    # ==========================================================================
    # - _cron_create_daily_attendance(): Cron job to create attendance
    #   records for all active courses every day
    # - _cron_send_absence_notifications(): Send notifications for absent students
    # ==========================================================================
    
    @api.model
    def _cron_create_daily_attendance(self):
        """
        TODO: Cron job to create daily attendance records
        Creates attendance records for all students in all active courses
        """
        # YOUR CODE HERE
        pass
    
    # TODO: Implement _cron_send_absence_notifications
    
    
    # ==========================================================================
    # TODO 9: Implement Reporting Methods
    # ==========================================================================
    # - get_attendance_report(date_from, date_to, course_id=None):
    #   Returns aggregated attendance data for reporting
    # - get_student_attendance_percentage(student_id, course_id=None):
    #   Returns attendance percentage for a student
    # ==========================================================================
    
    @api.model
    def get_attendance_report(self, date_from, date_to, course_id=None):
        """
        TODO: Generate attendance report data
        Use read_group for efficient aggregation
        """
        domain = [
            ('date', '>=', date_from),
            ('date', '<=', date_to),
        ]
        if course_id:
            domain.append(('course_id', '=', course_id))
        
        # YOUR CODE HERE - Use read_group to aggregate data
        
        return {
            'total_records': 0,
            'present_count': 0,
            'absent_count': 0,
            'late_count': 0,
            'attendance_rate': 0.0,
        }
    
    # TODO: Implement get_student_attendance_percentage
