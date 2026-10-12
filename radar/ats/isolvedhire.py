"""iSolvedHire：与 ApplicantPro 同一平台，见 applicantpro.py。"""
from .applicantpro import fetch_platform


def fetch(slug, meta=None):
    return fetch_platform(slug, "isolvedhire.com", '{"isInternal":0}', "isolvedhire")
