"""Exceptions"""

class SASEError(Exception):
    """Prisma SASE Error"""

class SASEAuthError(SASEError):
    """Authorization Error"""

class SASEMissingParam(SASEError):
    """Missing parameters"""

class SASENoBandwidthAllocation(SASEError):
    """No Allocated Bandwidth Associated"""

class SASEBadRequest(SASEError):
    """Bad Request 400 error"""

class SASEBadParam(SASEError):
    """Bad Parameter provided"""

class SASECommitError(SASEError):
    """Commit Error"""

class SASEMissingIkeOrIpsecProfile(SASEMissingParam):
    """Missing IKE or IPSEC Profile"""

class SASEObjectError(SASEError):
    """Generic Object Error"""

class SASEObjectExists(SASEObjectError):
    """Object already exists"""
