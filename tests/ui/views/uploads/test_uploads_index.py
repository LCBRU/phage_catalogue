import pytest
from flask import url_for
from lbrc_flask.pytest.asserts import assert__search_html, assert__requires_login, assert__requires_role
from lbrc_flask.pytest.html_content import get_records_found
from tests.requests import phage_catalogue_get
from lbrc_flask.pytest.testers import RequiresLoginTester, RequiresRoleTester, TableContentAsserter, IndexTester, PagedResultSet, RowContentAsserter
from phage_catalogue.security import ROLENAME_EDITOR, ROLENAME_UPLOADER, init_authorization


class UploadListTester:
    @property
    def endpoint(self):
        return 'ui.uploads_index'

    @pytest.fixture(autouse=True)
    def set_existing(self, client, faker, standard_lookups):
        ...


class UploadRowContentAsserter(TableContentAsserter):
    def assert_row_details(self, row, expected_result):
        assert row is not None
        assert expected_result is not None


class TestUploadListRequiresLogin(UploadListTester, RequiresLoginTester):
    ...


class TestUploadListRequiresUploader(UploadListTester, RequiresRoleTester):
    @property
    def user_with_required_role(self):
        return self.faker.user().get(save=True, rolename=ROLENAME_UPLOADER)

    @property
    def user_without_required_role(self):
        return self.faker.user().get(save=True)


class TestStudyList(UploadListTester, IndexTester):
    def user_to_login(self, faker):
        return faker.user().get(save=True, rolename=ROLENAME_UPLOADER)

    @property
    def content_asserter(self) -> RowContentAsserter:
        return UploadRowContentAsserter

    @pytest.mark.parametrize("item_count", PagedResultSet.test_page_edges())
    @pytest.mark.parametrize("current_page", PagedResultSet.test_current_pages())
    def test__get__no_filters(self, item_count, current_page):
        phages = self.faker.upload().get_list(save=True, item_count=item_count)

        self.parameters['page'] = current_page

        resp = self.get()

        self.assert_all(
            page_count_helper=PagedResultSet(page=current_page, expected_results=phages),
            resp=resp,
        )

    @pytest.mark.parametrize("item_count", PagedResultSet.test_page_edges())
    @pytest.mark.parametrize("current_page", PagedResultSet.test_current_pages())
    def test__get__no_filters(self, item_count, current_page):
        phages = self.faker.upload().get_list(save=True, 
            filename='somthing.xslx',
            item_count=item_count,
        )
        _ = self.faker.upload().get(save=True, filename='somthing_else.xslx')

        self.parameters['page'] = current_page

        self.parameters['search'] = 'somthing.xslx'

        resp = self.get()

        self.assert_all(
            page_count_helper=PagedResultSet(page=current_page, expected_results=phages),
            resp=resp,
        )
