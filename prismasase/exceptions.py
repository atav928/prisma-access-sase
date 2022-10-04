"""Exceptions"""

class SASEError(Exception):
    """Prisma SASE Error"""

class SASEAuthError(SASEError):
    """Authorization Error"""
