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
    # TODO: Add remaining basic fields
    
    
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
    
    # TODO: Add remaining computed fields
    
    @api.depends('enrollment_ids', 'enrollment_ids.state')
    def _compute_enrollment_stats(self):
        """
        TODO: Implement enrollment statistics computation
        Calculate enrolled_count, available_seats, is_full
        """
        for record in self:
            # YOUR CODE HERE
            record.enrolled_count = 0
    
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
        # YOUR CODE HERE
    ]
    
    # YOUR CODE HERE - Python constraints
    
    
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
        """TODO: Implement plan action"""
        for record in self:
            # YOUR CODE HERE
            pass
    
    # TODO: Implement remaining action methods
    
    
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
        return self.env['school.student']
    
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
    # TODO: Add remaining fields
    
    # TODO: Implement _compute_complete_name
    
    # TODO: Add SQL constraint for parent not being self


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
    # TODO: Add remaining fields
