# -*- coding: utf-8 -*-
# =============================================================================
# GRADE MODEL
# =============================================================================
# This model handles student grades for courses.
# Complete all TODO items to implement the full functionality.
# =============================================================================

from datetime import date

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError


class SchoolGrade(models.Model):
    """
    Grade Model
    
    Tracks grades/scores for students in courses.
    
    Concepts covered:
    - Float field with digits precision
    - Selection computed from score
    - Related fields usage
    - Aggregation with read_group
    """
    _name = 'school.grade'
    _description = 'Student Grade'
    _inherit = ['mail.thread']
    _order = 'date desc, id desc'
    _rec_name = 'display_name'
    
    # ==========================================================================
    # TODO 1: Define Basic Fields
    # ==========================================================================
    # Add the following fields:
    # - date: Date, required, default=today
    # - score: Float, required, digits=(5, 2)
    # - max_score: Float, required, default=100, digits=(5, 2)
    # - weight: Float, default=1.0 (for weighted average calculations)
    # - grade_type: Selection (exam, quiz, assignment, project, participation, final)
    # - description: Char (e.g., "Midterm Exam", "Quiz 1")
    # - feedback: Text (teacher's feedback)
    # ==========================================================================
    
    # YOUR CODE HERE - Basic Fields
    date = fields.Date(
        string='Date',
        required=True,
        default=fields.Date.today,
    )
    score = fields.Float(string='Score', required=True, digits=(5, 2))
    max_score = fields.Float(string='Max Score', required=True, default=100, digits=(5, 2))
    weight = fields.Float(string='Weight', default=1.0)
    grade_type = fields.Selection([
        ('exam', 'Exam'),
        ('quiz', 'Quiz'),
        ('assignment', 'Assignment'),
        ('project', 'Project'),
        ('participation', 'Participation'),
        ('final', 'Final'),
    ], string='Type')
    description = fields.Char(string='Description')
    feedback = fields.Text(string='Feedback')
    
    
    # ==========================================================================
    # TODO 2: Define Relational Fields
    # ==========================================================================
    # - student_id: Many2one to 'school.student', required, ondelete='cascade'
    # - course_id: Many2one to 'school.course', required, ondelete='cascade'
    # - teacher_id: Many2one to 'school.teacher' (who gave the grade)
    # - enrollment_id: Many2one to 'school.enrollment' (find matching enrollment)
    # ==========================================================================
    
    # YOUR CODE HERE - Relational Fields
    student_id = fields.Many2one('school.student', string='Student', required=True, ondelete='cascade')
    course_id = fields.Many2one('school.course', string='Course', required=True, ondelete='cascade')
    teacher_id = fields.Many2one('school.teacher', string='Teacher')
    enrollment_id = fields.Many2one('school.enrollment', string='Enrollment')
    
    
    # ==========================================================================
    # TODO 3: Define Computed Fields
    # ==========================================================================
    # - display_name: Computed as "Student - Course - Type (Score)"
    # - percentage: Float, computed as (score / max_score) * 100
    # - letter_grade: Selection, computed from percentage:
    #   * A: >= 90
    #   * B: >= 80
    #   * C: >= 70
    #   * D: >= 60
    #   * F: < 60
    # - is_passing: Boolean, True if percentage >= 60
    # - weighted_score: Float, score * weight
    # ==========================================================================
    
    display_name = fields.Char(
        string='Display Name',
        compute='_compute_display_name',
        store=True,
    )
    
    percentage = fields.Float(
        string='Percentage',
        compute='_compute_percentage',
        store=True,
        digits=(5, 2),
    )
    
    letter_grade = fields.Selection(
        selection=[
            ('A', 'A (Excellent)'),
            ('B', 'B (Good)'),
            ('C', 'C (Average)'),
            ('D', 'D (Below Average)'),
            ('F', 'F (Failing)'),
        ],
        string='Letter Grade',
        compute='_compute_letter_grade',
        store=True,
    )
    
    # TODO: Add remaining computed fields (is_passing, weighted_score)
    is_passing = fields.Boolean(string='Is Passing', compute='_compute_is_passing', store=True)
    weighted_score = fields.Float(string='Weighted Score', compute='_compute_weighted_score', store=True, digits=(5, 2))
    
    @api.depends('student_id', 'course_id', 'grade_type', 'score')
    def _compute_display_name(self):
        """TODO: Implement display name"""
        for record in self:
            record.display_name = f"{record.student_id.name} - {record.course_id.name} - {record.grade_type or ''} ({record.score})"
    
    @api.depends('score', 'max_score')
    def _compute_percentage(self):
        """TODO: Compute percentage from score and max_score"""
        for record in self:
            if record.max_score > 0:
                record.percentage = (record.score / record.max_score) * 100
            else:
                record.percentage = 0.0
    
    @api.depends('percentage')
    def _compute_letter_grade(self):
        """TODO: Compute letter grade from percentage"""
        for record in self:
            if record.percentage >= 90:
                record.letter_grade = 'A'
            elif record.percentage >= 80:
                record.letter_grade = 'B'
            elif record.percentage >= 70:
                record.letter_grade = 'C'
            elif record.percentage >= 60:
                record.letter_grade = 'D'
            else:
                record.letter_grade = 'F'
    
    @api.depends('percentage')
    def _compute_is_passing(self):
        """Check if grade is passing"""
        for record in self:
            record.is_passing = record.percentage >= 60
    
    @api.depends('score', 'weight')
    def _compute_weighted_score(self):
        """Compute weighted score"""
        for record in self:
            record.weighted_score = record.score * record.weight
    
    # TODO: Implement remaining compute methods
    
    
    # ==========================================================================
    # TODO 4: Define Constraints
    # ==========================================================================
    # SQL Constraints:
    # - check_score: score must be >= 0
    # - check_max_score: max_score must be > 0
    # - check_score_max: score must be <= max_score
    # - check_weight: weight must be > 0
    #
    # Python Constraints:
    # - Student must be enrolled in the course to receive a grade
    # - Date cannot be in the future
    # ==========================================================================
    
    _sql_constraints = [
        ('check_score', 'CHECK(score >= 0)', 'Score cannot be negative!'),
        ('check_max_score', 'CHECK(max_score > 0)', 'Max score must be positive!'),
        ('check_score_max', 'CHECK(score <= max_score)', 'Score cannot exceed max score!'),
        ('check_weight', 'CHECK(weight > 0)', 'Weight must be positive!'),
    ]
    
    @api.constrains('student_id', 'course_id')
    def _check_enrollment(self):
        """Validate student is enrolled in the course"""
        for record in self:
            if record.student_id and record.course_id:
                enrollment = self.env['school.enrollment'].search([
                    ('student_id', '=', record.student_id.id),
                    ('course_id', '=', record.course_id.id),
                ])
                if not enrollment:
                    raise ValidationError('Student is not enrolled in this course!')
    
    @api.constrains('date')
    def _check_date_not_future(self):
        """Validate date is not in the future"""
        from datetime import date as dt_date
        for record in self:
            if record.date > dt_date.today():
                raise ValidationError('Grade date cannot be in the future!')
    
    
    # ==========================================================================
    # TODO 5: Override CRUD Methods
    # ==========================================================================
    # - create(): Validate enrollment exists, set teacher from course
    # - write(): Track score changes in chatter
    # - unlink(): Prevent deletion of old grades (more than 30 days old)
    # ==========================================================================
    
    @api.model_create_multi
    def create(self, vals_list):
        """Validate and create grades"""
        from datetime import date as dt_date, timedelta
        for vals in vals_list:
            if 'student_id' in vals and 'course_id' in vals:
                # Find enrollment
                enrollment = self.env['school.enrollment'].search([
                    ('student_id', '=', vals['student_id']),
                    ('course_id', '=', vals['course_id']),
                ], limit=1)
                if enrollment:
                    vals['enrollment_id'] = enrollment.id
                # Set teacher from course if not provided
                if 'teacher_id' not in vals or not vals['teacher_id']:
                    course = self.env['school.course'].browse(vals['course_id'])
                    if course.teacher_id:
                        vals['teacher_id'] = course.teacher_id.id
        return super().create(vals_list)
    
    def write(self, vals):
        """Track score changes"""
        result = super().write(vals)
        if 'score' in vals:
            for record in self:
                record.message_post(body=f'Score changed to: {vals["score"]}')
        return result
    
    def unlink(self):
        """Prevent deletion of old grades"""
        from datetime import date as dt_date, timedelta
        for record in self:
            if (dt_date.today() - record.date).days > 30:
                raise UserError('Cannot delete grades older than 30 days!')
        return super().unlink()
    
    # YOUR CODE HERE - CRUD overrides
    
    
    # ==========================================================================
    # TODO 6: Implement Business Methods
    # ==========================================================================
    # - recalculate_letter_grade(): Force recomputation of letter grade
    # - get_grade_statistics(): Returns dict with min, max, avg for course
    # - compare_to_class_average(): Returns difference from class average
    # ==========================================================================
    
    def get_grade_statistics(self):
        """
        TODO: Get grade statistics for the course
        Use read_group for aggregation
        Return dict with: count, average, min, max
        """
        self.ensure_one()
        # Use read_group for efficient aggregation
        result = self.env['school.grade'].read_group(
            [('course_id', '=', self.course_id.id)],
            ['score:avg', 'score:min', 'score:max'],
            []
        )
        
        if result:
            stats = result[0]
            return {
                'count': len(self.course_id.grade_ids),
                'average': stats.get('score', 0.0),
                'min': stats.get('__range', {}).get('score', {}).get('min', 0.0),
                'max': stats.get('__range', {}).get('score', {}).get('max', 0.0),
            }
        
        return {
            'count': 0,
            'average': 0.0,
            'min': 0.0,
            'max': 0.0,
        }
    
    # TODO: Implement remaining methods
    
    
    # ==========================================================================
    # TODO 7: Implement Class Methods
    # ==========================================================================
    # - calculate_course_average(course_id): Returns average grade for a course
    # - calculate_student_gpa(student_id): Returns GPA for a student
    # - get_top_students(course_id, limit=10): Returns top students in a course
    # ==========================================================================
    
    @api.model
    def calculate_course_average(self, course_id):
        """
        TODO: Calculate average grade for a course
        Use search and aggregate methods
        """
        grades = self.search([('course_id', '=', course_id)])
        if not grades:
            return 0.0
        total = sum(grade.score for grade in grades)
        return total / len(grades)
    
    # TODO: Implement remaining class methods
