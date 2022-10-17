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

class SASEMissingIkeOrIpsecProfile(SASEMissingParam):
    """Missing IKE or IPSEC Profile"""
