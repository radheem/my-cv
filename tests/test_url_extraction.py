import pytest
import re
from engine.workflows.gmail_ingest import parse_and_normalize_job_url, extract_urls_from_text

def test_parse_and_normalize_linkedin_urls():
    # Standard view URL
    res = parse_and_normalize_job_url("https://www.linkedin.com/jobs/view/123456789")
    assert res["job_id"] == "123456789"
    assert res["platform"] == "linkedin"
    assert res["normalized_url"] == "https://www.linkedin.com/jobs/view/123456789/"

    # Subdomain/comm/tracking parameter
    res = parse_and_normalize_job_url("https://www.linkedin.com/comm/jobs/view/4428933791?trackingId=abc")
    assert res["job_id"] == "4428933791"
    assert res["platform"] == "linkedin"
    assert res["normalized_url"] == "https://www.linkedin.com/jobs/view/4428933791/"

    # Param query
    res = parse_and_normalize_job_url("https://www.linkedin.com/jobs/search/?currentJobId=4428933791")
    assert res["job_id"] == "4428933791"
    assert res["platform"] == "linkedin"
    assert res["normalized_url"] == "https://www.linkedin.com/jobs/view/4428933791/"


def test_parse_and_normalize_fraunhofer_urls():
    res = parse_and_normalize_job_url("https://jobs.fraunhofer.de/job/Ilmenau-Research-Associate-Secure-Development-98693/1234567/")
    assert res["job_id"] == "1234567"
    assert res["platform"] == "fraunhofer"
    assert res["normalized_url"] == "https://jobs.fraunhofer.de/job/Ilmenau-Research-Associate-Secure-Development-98693/1234567/"


def test_parse_and_normalize_glassdoor_urls():
    # Query param jl
    res = parse_and_normalize_job_url("https://www.glassdoor.com/job-listing/foo.htm?jl=100812345678")
    assert res["job_id"] == "100812345678"
    assert res["platform"] == "glassdoor"
    assert res["normalized_url"] == "https://www.glassdoor.com/job-listing/detail.htm?jl=100812345678"

    # Query param jobListingId
    res = parse_and_normalize_job_url("https://www.glassdoor.com/partner/jobListing.htm?jobListingId=1009123456789")
    assert res["job_id"] == "1009123456789"
    assert res["platform"] == "glassdoor"
    assert res["normalized_url"] == "https://www.glassdoor.com/job-listing/detail.htm?jl=1009123456789"


def test_parse_and_normalize_indeed_urls():
    res = parse_and_normalize_job_url("https://www.indeed.com/rc/clk?jk=123456789abcdef")
    assert res["job_id"] == "123456789abcdef"
    assert res["platform"] == "indeed"
    assert res["normalized_url"] == "https://www.indeed.com/viewjob?jk=123456789abcdef"


def test_parse_and_normalize_fallback():
    res = parse_and_normalize_job_url("https://www.google.com/careers/somejob")
    assert len(res["job_id"]) == 12  # MD5 hash of 12 chars
    assert res["platform"] == "other"
    assert res["normalized_url"] == "https://www.google.com/careers/somejob"


def test_extract_urls_from_text_multiple_platforms():
    text = (
        "Check out these opportunities:\n"
        "1. LinkedIn: https://www.linkedin.com/comm/jobs/view/4428933791?trackingId=abc.\n"
        "2. Glassdoor: https://www.glassdoor.com/partner/jobListing.htm?jobListingId=1009123456789,\n"
        "3. Indeed: https://www.indeed.com/rc/clk?jk=123456789abcdef!\n"
    )
    extracted = extract_urls_from_text(text)
    assert "https://www.linkedin.com/jobs/view/4428933791/" in extracted
    assert "https://www.glassdoor.com/job-listing/detail.htm?jl=1009123456789" in extracted
    assert "https://www.indeed.com/viewjob?jk=123456789abcdef" in extracted
    assert len(extracted) == 3


def test_extract_urls_filters_non_job_links():
    text = (
        "Check out this mail: https://www.linkedin.com/comm/jobs/alerts?lipi=urn%3Ali%3Apage\n"
        "And unsubscribe here: https://www.linkedin.com/job-alert-email-batch-unsubscribe\n"
        "Or get help: https://www.linkedin.com/help/linkedin/answer/4788\n"
    )
    extracted = extract_urls_from_text(text)
    assert len(extracted) == 0
