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
    # TODO: Add remaining basic fields
    
    
    # ==========================================================================
    # TODO 2: Define Relational Fields
    # ==========================================================================
    # - student_id: Many2one to 'school.student', required, ondelete='cascade'
    # - course_id: Many2one to 'school.course', required, ondelete='cascade'
    # - teacher_id: Many2one to 'school.teacher' (who gave the grade)
    # - enrollment_id: Many2one to 'school.enrollment' (find matching enrollment)
    # ==========================================================================
    
    # YOUR CODE HERE - Relational Fields
    
    
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
    
    @api.depends('student_id', 'course_id', 'grade_type', 'score')
    def _compute_display_name(self):
        """TODO: Implement display name"""
        for record in self:
            # YOUR CODE HERE
            record.display_name = ''
    
    @api.depends('score', 'max_score')
    def _compute_percentage(self):
        """TODO: Compute percentage from score and max_score"""
        for record in self:
            # YOUR CODE HERE
            record.percentage = 0.0
    
    @api.depends('percentage')
    def _compute_letter_grade(self):
        """TODO: Compute letter grade from percentage"""
        for record in self:
            # YOUR CODE HERE
            record.letter_grade = 'F'
    
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
        # TODO: Add remaining constraints
    ]
    
    @api.constrains('student_id', 'course_id')
    def _check_enrollment(self):
        """TODO: Validate student is enrolled in the course"""
        for record in self:
            # YOUR CODE HERE
            pass
    
    # TODO: Implement remaining constraints
    
    
    # ==========================================================================
    # TODO 5: Override CRUD Methods
    # ==========================================================================
    # - create(): Validate enrollment exists, set teacher from course
    # - write(): Track score changes in chatter
    # - unlink(): Prevent deletion of old grades (more than 30 days old)
    # ==========================================================================
    
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
        # YOUR CODE HERE - Use read_group for efficient aggregation
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
        # YOUR CODE HERE
        return 0.0
    
    # TODO: Implement remaining class methods
