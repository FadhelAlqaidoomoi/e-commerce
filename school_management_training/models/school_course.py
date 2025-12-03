# -*- coding: utf-8 -*-
# =============================================================================
# COURSE MODEL
# =============================================================================
# This model represents courses offered by the school.
# Complete all TODO items to implement the full functionality.
# =============================================================================

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError


class SchoolCourse(models.Model):
    """
    Course Model
    
    Concepts covered:
    - Default values with context
    - Domain constraints on fields
    - Recursive relationships (prerequisites)
    - Inverse fields
    - Method decorators (@api.model, @api.depends, etc.)
    """
    _name = 'school.course'
    _description = 'Course'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'code asc'
    
    # ==========================================================================
    # TODO 1: Define Basic Fields
    # ==========================================================================
    # Add the following fields:
    # - code: Char field, required, size=10
    # - name: Char field, required, tracking=True, translate=True
    # - description: Html field, translate=True
    # - credits: Integer field, required, default=3
    # - max_students: Integer field, default=30
    # - min_students: Integer field, default=5
    # - hours_per_week: Float field, digits=(4, 1)
    # - is_mandatory: Boolean field
    # - level: Selection (beginner, intermediate, advanced)
    # - start_date: Date field
    # - end_date: Date field
    # - active: Boolean, default=True
    # ==========================================================================
    
    # YOUR CODE HERE - Basic Fields
    code = fields.Char(
        string='Course Code',
        required=True,
        size=10,
        tracking=True,
    )
    name = fields.Char(string='Course Name', required=True, tracking=True, translate=True)
    description = fields.Html(string='Description', translate=True)
    credits = fields.Integer(string='Credits', required=True, default=3)
    max_students = fields.Integer(string='Max Students', default=30)
    min_students = fields.Integer(string='Min Students', default=5)
    hours_per_week = fields.Float(string='Hours Per Week', digits=(4, 1))
    is_mandatory = fields.Boolean(string='Is Mandatory')
    level = fields.Selection([
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
    ], string='Level')
    start_date = fields.Date(string='Start Date')
    end_date = fields.Date(string='End Date')
    active = fields.Boolean(string='Active', default=True)
    
    
    # ==========================================================================
    # TODO 2: Define Relational Fields
    # ==========================================================================
    # Add the following fields:
    # - teacher_id: Many2one to 'school.teacher', tracking=True
    # - enrollment_ids: One2many to 'school.enrollment' (inverse: course_id)
    # - student_ids: Many2many to 'school.student' (computed or through relation)
    # - grade_ids: One2many to 'school.grade' (inverse: course_id)
    # - prerequisite_ids: Many2many to 'school.course' (self-referential for prerequisites)
    # - category_id: Many2one to 'school.course.category'
    # - tag_ids: Many2many to 'school.course.tag'
    # ==========================================================================
    
    # YOUR CODE HERE - Relational Fields
    teacher_id = fields.Many2one('school.teacher', string='Teacher', tracking=True)
    enrollment_ids = fields.One2many('school.enrollment', 'course_id', string='Enrollments')
    student_ids = fields.Many2many('school.student', string='Students')
    grade_ids = fields.One2many('school.grade', 'course_id', string='Grades')
    prerequisite_ids = fields.Many2many('school.course', 'school_course_prerequisites_rel', 
        'course_id', 'prerequisite_id', string='Prerequisites')
    category_id = fields.Many2one('school.course.category', string='Category')
    tag_ids = fields.Many2many('school.course.tag', string='Tags')
    # ==========================================================================
    # TODO 3: Define State Field with Workflow
    # ==========================================================================
    # Add state field with states:
    # - draft: Draft
    # - planned: Planned  
    # - in_progress: In Progress
    # - completed: Completed
    # - cancelled: Cancelled
    # ==========================================================================
    
    # YOUR CODE HERE - State Field
    state = fields.Selection([
        ('draft', 'Draft'),
        ('planned', 'Planned'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ], string='State', default='draft', tracking=True)
    # ==========================================================================
    # TODO 4: Define Computed Fields
    # ==========================================================================
    # Implement:
    # - enrolled_count: Integer, count of confirmed enrollments
    # - available_seats: Integer, max_students - enrolled_count
    # - is_full: Boolean, True if available_seats <= 0
    # - progress_percentage: Float, percentage of course completion based on dates
    # - average_grade: Float, average of all grades for this course
    # ==========================================================================
    
    enrolled_count = fields.Integer(
        string='Enrolled Students',
        compute='_compute_enrollment_stats',
        store=True,
    )
    available_seats = fields.Integer(
        string='Available Seats',
        compute='_compute_enrollment_stats',
        store=True,
    )
    is_full = fields.Boolean(
        string='Is Full',
        compute='_compute_enrollment_stats',
        store=True,
    )
    progress_percentage = fields.Float(
        string='Progress %',
        compute='_compute_progress_percentage',
        digits=(5, 2),
        store=True,
    )
    average_grade = fields.Float(
        string='Average Grade',
        compute='_compute_average_grade',
        digits=(5, 2),
        store=True,
    )
    grade_count = fields.Integer(
        string='Grade Count',
        compute='_compute_grade_count',
        store=True,
    )
    
    # TODO: Add remaining computed fields
    
    @api.depends('enrollment_ids', 'enrollment_ids.state', 'max_students')
    def _compute_enrollment_stats(self):
        """
        TODO: Implement enrollment statistics computation
        Calculate enrolled_count, available_seats, is_full
        """
        for record in self:
            confirmed_enrollments = record.enrollment_ids.filtered(lambda e: e.state == 'confirmed')
            record.enrolled_count = len(confirmed_enrollments)
            record.available_seats = record.max_students - record.enrolled_count
            record.is_full = record.available_seats <= 0
    
    @api.depends('start_date', 'end_date')
    def _compute_progress_percentage(self):
        """Compute course progress based on dates"""
        from datetime import date as dt_date
        for record in self:
            if record.start_date and record.end_date:
                today = dt_date.today()
                total_days = (record.end_date - record.start_date).days
                elapsed_days = (today - record.start_date).days
                if total_days > 0:
                    record.progress_percentage = min(100.0, (elapsed_days / total_days) * 100)
                else:
                    record.progress_percentage = 0.0
            else:
                record.progress_percentage = 0.0
    
    @api.depends('grade_ids.score', 'grade_ids.max_score')
    def _compute_average_grade(self):
        """Compute average grade for the course"""
        for record in self:
            if record.grade_ids:
                percentages = [
                    (grade.score / grade.max_score * 100) if grade.max_score > 0 else 0
                    for grade in record.grade_ids
                ]
                record.average_grade = sum(percentages) / len(percentages) if percentages else 0.0
            else:
                record.average_grade = 0.0
    
    @api.depends('grade_ids')
    def _compute_grade_count(self):
        """Compute the count of grades for this course"""
        for record in self:
            record.grade_count = len(record.grade_ids)
    
    # TODO: Implement remaining compute methods
    
    
    # ==========================================================================
    # TODO 5: Define Constraints
    # ==========================================================================
    # SQL Constraints:
    # - unique_code: code must be unique
    # - check_credits: credits must be between 1 and 10
    # - check_max_students: max_students must be positive
    #
    # Python Constraints:
    # - end_date must be after start_date
    # - min_students must be less than max_students
    # - prerequisites cannot include self
    # ==========================================================================
    
    _sql_constraints = [
        ('unique_code', 'UNIQUE(code)', 'Course code must be unique!'),
        ('check_credits', 'CHECK(credits >= 1 AND credits <= 10)', 'Credits must be between 1 and 10!'),
        ('check_max_students', 'CHECK(max_students > 0)', 'Max students must be positive!'),
    ]
    
    @api.constrains('start_date', 'end_date')
    def _check_dates(self):
        """Validate end_date is after start_date"""
        for record in self:
            if record.start_date and record.end_date:
                if record.end_date < record.start_date:
                    raise ValidationError('End date must be after start date!')
    
    @api.constrains('min_students', 'max_students')
    def _check_students(self):
        """Validate min_students < max_students"""
        for record in self:
            if record.min_students >= record.max_students:
                raise ValidationError('Minimum students must be less than maximum students!')
    
    @api.constrains('prerequisite_ids')
    def _check_prerequisites(self):
        """Validate prerequisites do not include self"""
        for record in self:
            if record.prerequisite_ids.filtered(lambda p: p.id == record.id):
                raise ValidationError('A course cannot be a prerequisite for itself!')
    # ==========================================================================
    # TODO 6: Implement State Transition Methods
    # ==========================================================================
    # - action_plan(): draft -> planned (requires teacher_id)
    # - action_start(): planned -> in_progress (requires min_students enrolled)
    # - action_complete(): in_progress -> completed
    # - action_cancel(): any -> cancelled (unless completed)
    # - action_reset_draft(): cancelled -> draft
    # ==========================================================================
    
    def action_plan(self):
        """Plan the course"""
        for record in self:
            if not record.teacher_id:
                raise UserError('Course must have a teacher assigned before planning!')
            record.state = 'planned'
            record.message_post(body='Course has been planned')
    
    def action_start(self):
        """Start the course"""
        for record in self:
            if record.enrolled_count < record.min_students:
                raise UserError('Minimum number of students not met!')
            record.state = 'in_progress'
            record.message_post(body='Course has started')
    
    def action_complete(self):
        """Complete the course"""
        for record in self:
            record.state = 'completed'
            record.message_post(body='Course has been completed')
    
    def action_cancel(self):
        """Cancel the course"""
        for record in self:
            if record.state == 'completed':
                raise UserError('Cannot cancel a completed course!')
            record.state = 'cancelled'
            record.message_post(body='Course has been cancelled')
    
    def action_reset_draft(self):
        """Reset course to draft"""
        for record in self:
            record.state = 'draft'
            record.message_post(body='Course reset to draft')
    
    def action_view_enrollments(self):
        """Open the enrollments view for this course"""
        self.ensure_one()
        return {
            'name': _('Enrollments'),
            'type': 'ir.actions.act_window',
            'res_model': 'school.enrollment',
            'view_mode': 'list,form',
            'domain': [('course_id', '=', self.id)],
            'context': {'default_course_id': self.id},
        }
    
    def action_view_grades(self):
        """Open the grades view for this course"""
        self.ensure_one()
        return {
            'name': _('Grades'),
            'type': 'ir.actions.act_window',
            'res_model': 'school.grade',
            'view_mode': 'list,form',
            'domain': [('course_id', '=', self.id)],
            'context': {'default_course_id': self.id},
        }
    
    
    # ==========================================================================
    # TODO 7: Implement Business Methods
    # ==========================================================================
    # - get_eligible_students(): Returns students who meet prerequisites
    # - check_prerequisites(student): Returns True if student meets prerequisites
    # - get_schedule(): Returns schedule information
    # - clone_for_next_term(): Creates copy for next academic term
    # ==========================================================================
    
    def get_eligible_students(self):
        """TODO: Return students eligible to enroll (meet prerequisites)"""
        self.ensure_one()
        # If no prerequisites, all students are eligible
        if not self.prerequisite_ids:
            return self.env['school.student'].search([])
        
        # Find students who have completed prerequisite courses
        eligible_student_ids = set()
        for prereq in self.prerequisite_ids:
            for enrollment in prereq.enrollment_ids.filtered(lambda e: e.state == 'completed'):
                eligible_student_ids.add(enrollment.student_id.id)
        
        return self.env['school.student'].browse(list(eligible_student_ids))
    
    def check_prerequisites(self, student):
        """Check if a student meets prerequisites"""
        self.ensure_one()
        if not self.prerequisite_ids:
            return True
        
        for prereq in self.prerequisite_ids:
            completed = self.env['school.enrollment'].search([
                ('student_id', '=', student.id),
                ('course_id', '=', prereq.id),
                ('state', '=', 'completed'),
            ])
            if not completed:
                return False
        return True
    
    def clone_for_next_term(self):
        """Create a copy of this course for the next term"""
        self.ensure_one()
        from datetime import timedelta
        new_course = self.copy(default={
            'state': 'draft',
            'code': self.code + '_2',
            'enrollment_ids': [],
        })
        if self.start_date and self.end_date:
            days_duration = (self.end_date - self.start_date).days
            new_start = self.start_date + timedelta(days=365)
            new_end = new_start + timedelta(days=days_duration)
            new_course.write({
                'start_date': new_start,
                'end_date': new_end,
            })
        return new_course
    
    # TODO: Implement remaining methods


class SchoolCourseCategory(models.Model):
    """
    Course Category Model (for grouping courses)
    
    Concepts covered:
    - Parent/child hierarchy
    - Recursive name computation
    - Complete name with parent path
    """
    _name = 'school.course.category'
    _description = 'Course Category'
    _parent_name = 'parent_id'
    _parent_store = True
    _order = 'complete_name asc'
    
    # ==========================================================================
    # TODO 8: Define Category Fields
    # ==========================================================================
    # - name: Char, required
    # - parent_id: Many2one to self
    # - child_ids: One2many to self
    # - parent_path: Char (for parent_store)
    # - complete_name: Char, computed (shows full path like "Parent / Child")
    # - course_ids: One2many to 'school.course'
    # - course_count: Integer, computed count of courses
    # ==========================================================================
    
    name = fields.Char(string='Name', required=True)
    parent_id = fields.Many2one('school.course.category', string='Parent Category', ondelete='cascade')
    child_ids = fields.One2many('school.course.category', 'parent_id', string='Child Categories')
    parent_path = fields.Char(string='Parent Path', index=True)
    complete_name = fields.Char(string='Complete Name', compute='_compute_complete_name', store=True, recursive=True)
    course_ids = fields.One2many('school.course', 'category_id', string='Courses')
    course_count = fields.Integer(string='Course Count', compute='_compute_course_count', store=True)
    
    @api.depends('name', 'parent_id.complete_name')
    def _compute_complete_name(self):
        """Compute complete hierarchical name"""
        for record in self:
            if record.parent_id:
                record.complete_name = f"{record.parent_id.complete_name} / {record.name}"
            else:
                record.complete_name = record.name
    
    @api.depends('course_ids')
    def _compute_course_count(self):
        """Count courses in this category"""
        for record in self:
            record.course_count = len(record.course_ids)
    
    # TODO: Implement _compute_complete_name
    
    # TODO: Add SQL constraint for parent not being self
    _sql_constraints = [
        ('parent_not_self', 'CHECK(parent_id != id)', 'A category cannot be its own parent!'),
    ]


class SchoolCourseTag(models.Model):
    """
    Course Tags Model (for labeling courses)
    
    Concepts covered:
    - Simple tagging model
    - Color field for kanban
    """
    _name = 'school.course.tag'
    _description = 'Course Tag'
    _order = 'name asc'
    
    # ==========================================================================
    # TODO 9: Define Tag Fields
    # ==========================================================================
    # - name: Char, required
    # - color: Integer (for kanban color)
    # - course_ids: Many2many to 'school.course'
    # ==========================================================================
    
    name = fields.Char(string='Name', required=True)
    color = fields.Integer(string='Color')
    course_ids = fields.Many2many('school.course', string='Courses')
