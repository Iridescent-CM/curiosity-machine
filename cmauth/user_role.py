"""
    Class for defining users role.
"""

class Role:
    MENTOR = 1
    STUDENT =  2

    ALL_CHOICES = ((MENTOR, MENTOR),
                   (STUDENT, STUDENT))