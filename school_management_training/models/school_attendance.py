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
    check_in = fields.Datetime(string='Check In')
    check_out = fields.Datetime(string='Check Out')
    status = fields.Selection([
        ('present', 'Present'),
        ('absent', 'Absent'),
        ('late', 'Late'),
        ('excused', 'Excused'),
        ('half_day', 'Half Day'),
    ], string='Status', default='absent')
    remarks = fields.Text(string='Remarks')
    is_excused = fields.Boolean(string='Is Excused', default=False)
    
    
    # ==========================================================================
    # TODO 2: Define Relational Fields
    # ==========================================================================
    # - student_id: Many2one to 'school.student', required, ondelete='cascade'
    # - course_id: Many2one to 'school.course', required, ondelete='cascade'
    # - recorded_by: Many2one to 'res.users', default=current user
    # ==========================================================================
    
    # YOUR CODE HERE - Relational Fields
    student_id = fields.Many2one('school.student', string='Student', required=True, ondelete='cascade')
    course_id = fields.Many2one('school.course', string='Course', required=True, ondelete='cascade')
    recorded_by = fields.Many2one('res.users', string='Recorded By', default=lambda self: self.env.user)
    
    
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
    duration_hours = fields.Float(string='Duration Hours', compute='_compute_duration_hours', store=True, digits=(5, 2))
    is_on_time = fields.Boolean(string='Is On Time', compute='_compute_is_on_time', store=True)
    day_of_week = fields.Selection([
        ('0', 'Monday'),
        ('1', 'Tuesday'),
        ('2', 'Wednesday'),
        ('3', 'Thursday'),
        ('4', 'Friday'),
        ('5', 'Saturday'),
        ('6', 'Sunday'),
    ], string='Day of Week', compute='_compute_day_of_week', store=True)
    
    @api.depends('student_id', 'course_id', 'date', 'status')
    def _compute_display_name(self):
        """TODO: Implement display name"""
        for record in self:
            record.display_name = f"{record.student_id.name} - {record.course_id.name} - {record.date} ({record.status})"
    
    @api.depends('check_in', 'check_out')
    def _compute_duration_hours(self):
        """Compute duration in hours"""
        for record in self:
            if record.check_in and record.check_out:
                duration = record.check_out - record.check_in
                record.duration_hours = duration.total_seconds() / 3600.0
            else:
                record.duration_hours = 0.0
    
    @api.depends('check_in')
    def _compute_is_on_time(self):
        """Check if student checked in before 9:00 AM"""
        for record in self:
            if record.check_in:
                check_in_time = record.check_in.time()
                record.is_on_time = check_in_time.hour < 9
            else:
                record.is_on_time = False
    
    @api.depends('date')
    def _compute_day_of_week(self):
        """Get day of week"""
        for record in self:
            if record.date:
                record.day_of_week = str(record.date.weekday())
            else:
                record.day_of_week = '0'
    
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
            if record.check_in and record.check_out and record.check_out < record.check_in:
                raise ValidationError('Check out time cannot be before check in time!')
    
    @api.constrains('date')
    def _check_date_not_future(self):
        """Validate date is not in the future"""
        for record in self:
            if record.date > date.today():
                raise ValidationError('Attendance date cannot be in the future!')
    
    @api.constrains('student_id', 'course_id')
    def _check_enrollment(self):
        """Validate student is enrolled in the course"""
        for record in self:
            enrollment = self.env['school.enrollment'].search([
                ('student_id', '=', record.student_id.id),
                ('course_id', '=', record.course_id.id),
                ('state', '=', 'confirmed'),
            ])
            if not enrollment:
                raise ValidationError('Student is not enrolled in this course!')
    
    
    # ==========================================================================
    # TODO 5: Implement Onchange Methods
    # ==========================================================================
    # - _onchange_check_in: If check_in is after 9:00, suggest status='late'
    # - _onchange_status: If status is 'excused', set is_excused=True
    # ==========================================================================
    
    @api.onchange('check_in')
    def _onchange_check_in(self):
        """If check_in is after 9:00, suggest status='late'"""
        if self.check_in:
            check_in_time = self.check_in.time()
            if check_in_time.hour >= 9 and check_in_time.minute > 0:
                self.status = 'late'
    
    @api.onchange('status')
    def _onchange_status(self):
        """If status is 'excused', set is_excused=True"""
        if self.status == 'excused':
            self.is_excused = True
        elif self.status != 'absent':
            self.is_excused = False
    
    
    # ==========================================================================
    # TODO 6: Implement Business Methods
    # ==========================================================================
    # - mark_present(): Quick action to mark as present with current time
    # - mark_absent(): Quick action to mark as absent
    # - get_student_attendance_summary(student_id, date_from, date_to):
    #   Returns attendance statistics for a student in date range
    # ==========================================================================
    
    def mark_present(self):
        """Mark attendance as present with current time"""
        for record in self:
            record.status = 'present'
            if not record.check_in:
                record.check_in = datetime.now()
    
    def mark_absent(self):
        """Mark attendance as absent"""
        for record in self:
            record.status = 'absent'
    
    @api.model
    def get_student_attendance_summary(self, student_id, date_from, date_to):
        """Get attendance summary for student in date range"""
        records = self.search([
            ('student_id', '=', student_id),
            ('date', '>=', date_from),
            ('date', '<=', date_to),
        ])
        
        total = len(records)
        present = len(records.filtered(lambda r: r.status == 'present'))
        absent = len(records.filtered(lambda r: r.status == 'absent'))
        late = len(records.filtered(lambda r: r.status == 'late'))
        excused = len(records.filtered(lambda r: r.is_excused))
        
        return {
            'total': total,
            'present': present,
            'absent': absent,
            'late': late,
            'excused': excused,
            'rate': (present / total * 100) if total > 0 else 0.0,
        }
    
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
        
        course = self.env['school.course'].browse(course_id)
        enrollments = self.env['school.enrollment'].search([
            ('course_id', '=', course_id),
            ('state', '=', 'confirmed'),
        ])
        
        records_to_create = []
        for enrollment in enrollments:
            # Check if attendance already exists
            existing = self.search([
                ('student_id', '=', enrollment.student_id.id),
                ('course_id', '=', course_id),
                ('date', '=', attendance_date),
            ])
            
            if not existing:
                records_to_create.append({
                    'student_id': enrollment.student_id.id,
                    'course_id': course_id,
                    'date': attendance_date,
                    'status': 'absent',
                })
        
        if records_to_create:
            return self.create(records_to_create)
        
        return self.env['school.attendance']
    
    def bulk_mark_present(self, attendance_ids):
        """Mark multiple records as present"""
        records = self.env['school.attendance'].browse(attendance_ids)
        for record in records:
            record.mark_present()
    
    def bulk_mark_absent(self, attendance_ids):
        """Mark multiple records as absent"""
        records = self.env['school.attendance'].browse(attendance_ids)
        for record in records:
            record.mark_absent()
    
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
        active_courses = self.env['school.course'].search([('state', '=', 'in_progress')])
        for course in active_courses:
            self.bulk_create_attendance(course.id)
    
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
        
        records = self.search(domain)
        total = len(records)
        present = len(records.filtered(lambda r: r.status == 'present'))
        absent = len(records.filtered(lambda r: r.status == 'absent'))
        late = len(records.filtered(lambda r: r.status == 'late'))
        
        return {
            'total_records': total,
            'present_count': present,
            'absent_count': absent,
            'late_count': late,
            'attendance_rate': (present / total * 100) if total > 0 else 0.0,
        }
    
    @api.model
    def get_student_attendance_percentage(self, student_id, course_id=None):
        """Get attendance percentage for a student"""
        domain = [('student_id', '=', student_id)]
        if course_id:
            domain.append(('course_id', '=', course_id))
        
        records = self.search(domain)
        if not records:
            return 0.0
        
        present = len(records.filtered(lambda r: r.status == 'present'))
        return (present / len(records)) * 100 if records else 0.0
    
    # TODO: Implement get_student_attendance_percentage
