# -*- coding: utf-8 -*-
# =============================================================================
# TEACHER MODEL
# =============================================================================
# This model represents teachers in the school system.
# Complete all TODO items to implement the full functionality.
# =============================================================================

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError


class SchoolTeacher(models.Model):
    """
    Teacher Model
    
    Concepts covered:
    - Delegation inheritance (_inherits)
    - Related fields
    - Default values with lambda
    - Domain filters on relational fields
    - Monetary fields
    - Company-dependent fields
    """
    _name = 'school.teacher'
    _description = 'Teacher'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name asc'
    
    # ==========================================================================
    # TODO 1: Define Basic Fields
    # ==========================================================================
    # Add the following fields:
    # - employee_code: Char field, readonly, copy=False (auto-generated)
    # - name: Char field, required, tracking=True
    # - email: Char field, required
    # - phone: Char field
    # - date_of_birth: Date field
    # - hire_date: Date field, required, default=today
    # - department: Selection (science, arts, mathematics, languages, physical_education, other)
    # - qualification: Char field
    # - experience_years: Integer field with default 0
    # - biography: Html field
    # - photo: Binary field
    # - active: Boolean with default True
    # ==========================================================================
    
    # YOUR CODE HERE - Basic Fields
    employee_code = fields.Char(
        string='Employee Code',
        readonly=True,
        copy=False,
        default=lambda self: _('New'),
    )
    name = fields.Char(string='Name', required=True, tracking=True)
    email = fields.Char(string='Email', required=True)
    phone = fields.Char(string='Phone')
    date_of_birth = fields.Date(string='Date of Birth')
    hire_date = fields.Date(string='Hire Date', required=True, default=fields.Date.today)
    department = fields.Selection([
        ('science', 'Science'),
        ('arts', 'Arts'),
        ('mathematics', 'Mathematics'),
        ('languages', 'Languages'),
        ('physical_education', 'Physical Education'),
        ('other', 'Other'),
    ], string='Department')
    qualification = fields.Char(string='Qualification')
    experience_years = fields.Integer(string='Experience Years', default=0)
    biography = fields.Html(string='Biography')
    photo = fields.Binary(string='Photo')
    active = fields.Boolean(string='Active', default=True)
    
    
    # ==========================================================================
    # TODO 2: Define Monetary Field
    # ==========================================================================
    # Add salary field:
    # - salary: Monetary field
    # - currency_id: Many2one to 'res.currency' (use company's currency as default)
    # 
    # Hint: For monetary fields, you need both the monetary field and a currency field
    # ==========================================================================
    
    # YOUR CODE HERE - Monetary Fields
    currency_id = fields.Many2one('res.currency', string='Currency', 
        default=lambda self: self.env.user.company_id.currency_id)
    salary = fields.Monetary(string='Salary', currency_field='currency_id')
    # ==========================================================================
    # TODO 3: Define Relational Fields
    # ==========================================================================
    # Add the following relational fields:
    # - course_ids: One2many to 'school.course' (inverse: teacher_id)
    # - user_id: Many2one to 'res.users' (linked portal user)
    # - company_id: Many2one to 'res.company' with default
    # ==========================================================================
    
    # YOUR CODE HERE - Relational Fields
    course_ids = fields.One2many('school.course', 'teacher_id', string='Courses')
    user_id = fields.Many2one('res.users', string='Portal User')
    company_id = fields.Many2one('res.company', string='Company', 
        default=lambda self: self.env.user.company_id)
    # ==========================================================================
    # TODO 4: Define Computed Fields
    # ==========================================================================
    # Implement:
    # - total_courses: Integer, count of course_ids
    # - total_students: Integer, count of all students across all courses
    # - age: Integer, calculated from date_of_birth
    # - years_of_service: Integer, calculated from hire_date
    # ==========================================================================
    
    # YOUR CODE HERE - Computed Fields and their compute methods
    total_courses = fields.Integer(string='Total Courses', compute='_compute_total_courses', store=True)
    total_students = fields.Integer(string='Total Students', compute='_compute_total_students', store=True)
    age = fields.Integer(string='Age', compute='_compute_age', store=True)
    years_of_service = fields.Integer(string='Years of Service', compute='_compute_years_of_service', store=True)
    
    @api.depends('course_ids')
    def _compute_total_courses(self):
        """Count total courses taught"""
        for record in self:
            record.total_courses = len(record.course_ids)
    
    @api.depends('course_ids.enrollment_ids')
    def _compute_total_students(self):
        """Count total students across all courses"""
        for record in self:
            student_ids = set()
            for course in record.course_ids:
                for enrollment in course.enrollment_ids:
                    student_ids.add(enrollment.student_id.id)
            record.total_students = len(student_ids)
    
    @api.depends('date_of_birth')
    def _compute_age(self):
        """Calculate age from date of birth"""
        from datetime import date as dt_date
        for record in self:
            if record.date_of_birth:
                today = dt_date.today()
                record.age = today.year - record.date_of_birth.year - (
                    (today.month, today.day) < (record.date_of_birth.month, record.date_of_birth.day)
                )
            else:
                record.age = 0
    
    @api.depends('hire_date')
    def _compute_years_of_service(self):
        """Calculate years of service from hire date"""
        from datetime import date as dt_date
        for record in self:
            if record.hire_date:
                today = dt_date.today()
                record.years_of_service = today.year - record.hire_date.year
            else:
                record.years_of_service = 0
    # ==========================================================================
    # TODO 5: Define Related Fields
    # ==========================================================================
    # Add related fields:
    # - company_name: Char, related to company_id.name
    # - company_currency_id: Many2one, related to company_id.currency_id
    # ==========================================================================
    
    # YOUR CODE HERE - Related Fields
    company_name = fields.Char(string='Company Name', related='company_id.name', readonly=True)
    company_currency_id = fields.Many2one('res.currency', string='Company Currency', 
        related='company_id.currency_id', readonly=True)
    # ==========================================================================
    # TODO 6: Define SQL and Python Constraints
    # ==========================================================================
    # SQL Constraints:
    # - unique_employee_code: employee_code must be unique
    # - check_experience: experience_years must be >= 0
    #
    # Python Constraints:
    # - hire_date cannot be in the future
    # - salary must be positive if provided
    # ==========================================================================
    
    _sql_constraints = [
        ('unique_employee_code', 'UNIQUE(employee_code)', 'Employee code must be unique!'),
        ('check_experience', 'CHECK(experience_years >= 0)', 'Experience years cannot be negative!'),
    ]
    
    @api.constrains('hire_date')
    def _check_hire_date(self):
        """Validate hire date is not in the future"""
        from datetime import date as dt_date
        for record in self:
            if record.hire_date and record.hire_date > dt_date.today():
                raise ValidationError('Hire date cannot be in the future!')
    
    @api.constrains('salary')
    def _check_salary(self):
        """Validate salary is positive"""
        for record in self:
            if record.salary and record.salary < 0:
                raise ValidationError('Salary cannot be negative!')
    # ==========================================================================
    # TODO 7: Override create method
    # ==========================================================================
    # - Generate employee_code using sequence 'school.teacher.sequence'
    # - Post creation message
    # ==========================================================================
    
    @api.model_create_multi
    def create(self, vals_list):
        """TODO: Implement create override"""
        for vals in vals_list:
            if vals.get('employee_code', _('New')) == _('New'):
                vals['employee_code'] = self.env['ir.sequence'].next_by_code('school.teacher.sequence') or _('New')
        return super().create(vals_list)
    
    
    # ==========================================================================
    # TODO 8: Implement Business Methods
    # ==========================================================================
    # 
    # 8.1 get_courses_summary(): Returns dict with course statistics
    #
    # 8.2 assign_to_course(course_id): Assigns teacher to a course
    #     - Validate teacher is not already assigned
    #     - Update course's teacher_id
    #
    # 8.3 remove_from_course(course_id): Removes teacher from a course
    # ==========================================================================
    
    def get_courses_summary(self):
        """TODO: Implement course summary"""
        self.ensure_one()
        courses_list = []
        for course in self.course_ids:
            courses_list.append({
                'id': course.id,
                'name': course.name,
                'code': course.code,
                'enrolled_count': course.enrolled_count,
            })
        
        return {
            'total_courses': len(self.course_ids),
            'total_students': self.total_students,
            'courses': courses_list,
        }
    
    def assign_to_course(self, course_id):
        """Assign teacher to a course"""
        if self.course_ids.filtered(lambda c: c.id == course_id):
            raise UserError('Teacher is already assigned to this course!')
        
        course = self.env['school.course'].browse(course_id)
        course.teacher_id = self.id
    
    def remove_from_course(self, course_id):
        """Remove teacher from a course"""
        course = self.env['school.course'].browse(course_id)
        if course.teacher_id.id == self.id:
            course.teacher_id = None
    
    def action_view_courses(self):
        """Open the courses view for this teacher"""
        self.ensure_one()
        return {
            'name': _('Courses'),
            'type': 'ir.actions.act_window',
            'res_model': 'school.course',
            'view_mode': 'list,form',
            'domain': [('teacher_id', '=', self.id)],
            'context': {'default_teacher_id': self.id},
        }
    
    def action_view_students(self):
        """Open the students view for all courses taught by this teacher"""
        self.ensure_one()
        return {
            'name': _('Students'),
            'type': 'ir.actions.act_window',
            'res_model': 'school.student',
            'view_mode': 'list,form',
            'domain': [('enrollment_ids.course_id.teacher_id', '=', self.id)],
        }
    
    # TODO: Implement remaining methods
