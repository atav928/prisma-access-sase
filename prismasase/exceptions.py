"""Exceptions"""

class SASEError(Exception):
    """Prisma SASE Error"""

class SASEAuthError(SASEError):
    """Authorization Error"""

class SASEMissingParam(SASEError):
    """Missing parameters"""
