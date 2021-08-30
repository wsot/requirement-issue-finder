import pytest
import pathlib

from reqparser import Requirement, RequirementsParser


@pytest.fixture
def testfile():
    def get(filename):
        with open(pathlib.Path("./testfiles") / filename, "r") as f:
            return f.readlines()

    return get


class TestRequirementsParsing:
    def test_handle_some_requirements_have_conditions(self, testfile):
        parsed = RequirementsParser(testfile("requirements_somespecs.in")).parse()
        assert len(parsed) == 4
        r = parsed.pop(0)
        assert r.name == "django-filter"
        assert r.specs == [("==", "2.3.0")]
        r = parsed.pop(0)
        assert r.name == "django-health-check"
        assert r.specs == []
        r = parsed.pop(0)
        assert r.name == "graphene-django"
        assert r.specs == [("==", "2.13.0")]
        r = parsed.pop(0)
        assert r.name == "graphql-core"
        assert r.specs == [("==", "2.3.2")]

    def test_requirements_handle_header(self, testfile):
        parsed = RequirementsParser(testfile("requirements_header.txt")).parse()
        assert len(parsed) == 2

        r = parsed.pop(0)
        assert r.name == "graphene"
        assert r.specs == [("==", "2.1.9")]
        assert r.is_primary_dependency == False
        assert {reqfor.name for reqfor in r.requirement_for} == {"graphene-django"}

        r = parsed.pop(0)
        assert r.name == "graphene-django"
        assert r.specs == [("==", "2.13.0")]
        assert r.is_primary_dependency == True
        assert len(r.requirement_for) == 0

    def test_requirements_handle_footer_comments(self, testfile):
        parsed = RequirementsParser(testfile("requirements_footer.txt")).parse()
        assert len(parsed) == 2

        r = parsed.pop(0)
        assert r.name == "graphene"
        assert r.specs == [("==", "2.1.9")]
        assert r.is_primary_dependency == False
        assert {reqfor.name for reqfor in r.requirement_for} == {"graphene-django"}

        r = parsed.pop(0)
        assert r.name == "graphene-django"
        assert r.specs == [("==", "2.13.0")]
        assert r.is_primary_dependency == True
        assert len(r.requirement_for) == 0

    def test_requirements_handle_footer_comments(self, testfile):
        parsed = RequirementsParser(testfile("requirements_all.txt")).parse()
        assert len(parsed) == 16

        r = parsed.pop(0)
        assert r.name == "aniso8601"
        assert r.specs == [("==", "7.0.0")]
        assert r.is_primary_dependency == False
        assert {reqfor.name for reqfor in r.requirement_for} == {"graphene"}

        r = parsed.pop(0)
        assert r.name == "asgiref"
        assert r.specs == [("==", "3.4.1")]
        assert r.is_primary_dependency == False
        assert {reqfor.name for reqfor in r.requirement_for} == {"django"}

        r = parsed.pop(0)
        assert r.name == "django"
        assert r.specs == [("==", "3.2.6")]
        assert r.is_primary_dependency == False
        assert {reqfor.name for reqfor in r.requirement_for} == {"django-filter", "django-health-check", "graphene-django"}

        r = parsed.pop(0)
        assert r.name == "django-filter"
        assert r.specs == [("==", "2.3.0")]
        assert r.is_primary_dependency == True
        assert len(r.requirement_for) == 0

        r = parsed.pop(0)
        assert r.name == "django-health-check"
        assert r.specs == [("==", "3.16.4")]
        assert r.is_primary_dependency == True
        assert len(r.requirement_for) == 0

        r = parsed.pop(0)
        assert r.name == "graphene"
        assert r.specs == [("==", "2.1.9")]
        assert r.is_primary_dependency == False
        assert {reqfor.name for reqfor in r.requirement_for} == {"graphene-django"}

        r = parsed.pop(0)
        assert r.name == "graphene-django"
        assert r.specs == [("==", "2.13.0")]
        assert r.is_primary_dependency == True
        assert len(r.requirement_for) == 0

        r = parsed.pop(0)
        assert r.name == "graphql-core"
        assert r.specs == [("==", "2.3.2")]
        assert r.is_primary_dependency == True
        assert {reqfor.name for reqfor in r.requirement_for} == {"graphene", "graphene-django", "graphql-relay"}

        r = parsed.pop(0)
        assert r.name == "graphql-relay"
        assert r.specs == [("==", "2.0.1")]
        assert r.is_primary_dependency == False
        assert {reqfor.name for reqfor in r.requirement_for} == {"graphene"}

        r = parsed.pop(0)
        assert r.name == "promise"
        assert r.specs == [("==", "2.3")]
        assert r.is_primary_dependency == False
        assert {reqfor.name for reqfor in r.requirement_for} == {"graphene-django", "graphql-core", "graphql-relay"}

        r = parsed.pop(0)
        assert r.name == "pytz"
        assert r.specs == [("==", "2021.1")]
        assert r.is_primary_dependency == False
        assert {reqfor.name for reqfor in r.requirement_for} == {"django"}

        r = parsed.pop(0)
        assert r.name == "rx"
        assert r.specs == [("==", "1.6.1")]
        assert r.is_primary_dependency == False
        assert {reqfor.name for reqfor in r.requirement_for} == {"graphql-core"}

        r = parsed.pop(0)
        assert r.name == "singledispatch"
        assert r.specs == [("==", "3.7.0")]
        assert r.is_primary_dependency == False
        assert {reqfor.name for reqfor in r.requirement_for} == {"graphene-django"}

        r = parsed.pop(0)
        assert r.name == "six"
        assert r.specs == [("==", "1.16.0")]
        assert r.is_primary_dependency == False
        assert {reqfor.name for reqfor in r.requirement_for} == {"graphene-django", "graphene", "graphql-core", "graphql-relay", "promise", "singledispatch"}

        r = parsed.pop(0)
        assert r.name == "sqlparse"
        assert r.specs == [("==", "0.4.1")]
        assert r.is_primary_dependency == False
        assert {reqfor.name for reqfor in r.requirement_for} == {"django"}

        r = parsed.pop(0)
        assert r.name == "unidecode"
        assert r.specs == [("==", "1.2.0")]
        assert r.is_primary_dependency == False
        assert {reqfor.name for reqfor in r.requirement_for} == {"graphene-django"}
