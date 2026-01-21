import pytest
from phage_catalogue.services.specimens import get_type_choices
from phage_catalogue.services.lookups import get_bacterial_species_choices
from lbrc_flask.pytest.testers import RequiresLoginTester, PanelListContentAsserter, IndexTester, PagedResultSet, RowContentAsserter
from lbrc_flask.pytest.form_tester import FormTester, FormTesterDateField, FormTesterSelectField, FormTesterNumberField, FormTesterTextField


class SpecimenListTester:
    @property
    def endpoint(self):
        return 'ui.index'

    @pytest.fixture(autouse=True)
    def set_existing(self, client, faker, standard_lookups):
        ...


class SpecimenSearchFormTester(FormTester):
    def __init__(self, type_options=None, bacterial_species_options=None, has_csrf=False):
        type_options = type_options or {}
        bacterial_species_options = bacterial_species_options or {}

        super().__init__(
            fields=[
                FormTesterSelectField(
                    field_name='type',
                    field_title='Type',
                    options=type_options,
                ),
                FormTesterDateField(
                    field_name='start_date',
                    field_title='Start Date',
                ),
                FormTesterDateField(
                    field_name='end_date',
                    field_title='End Date',
                ),
                FormTesterNumberField(
                    field_name='freezer',
                    field_title='Freezer',
                ),
                FormTesterNumberField(
                    field_name='drawer',
                    field_title='Drawer',
                ),
                FormTesterTextField(
                    field_name='position',
                    field_title='Position',
                ),
                FormTesterTextField(
                    field_name='project',
                    field_title='Project',
                ),
                FormTesterTextField(
                    field_name='storage_method',
                    field_title='Storage Method',
                ),
                FormTesterTextField(
                    field_name='staff_member',
                    field_title='Staff Member',
                ),
                FormTesterSelectField(
                    field_name='species_id',
                    field_title='Bacterial Species',
                    options=bacterial_species_options,
                ),
                FormTesterTextField(
                    field_name='strain',
                    field_title='Strain',
                ),
                FormTesterTextField(
                    field_name='medium',
                    field_title='medium',
                ),
                FormTesterTextField(
                    field_name='plasmid',
                    field_title='plasmid',
                ),
                FormTesterTextField(
                    field_name='resistance_marker',
                    field_title='resistance_marker',
                ),
                FormTesterTextField(
                    field_name='phage_identifier',
                    field_title='phage_identifier',
                ),
                FormTesterSelectField(
                    field_name='host_id',
                    field_title='Phage Host',
                    options=bacterial_species_options,
                ),
            ],
            has_csrf=has_csrf,
        )


class SpecimenRowContentAsserter(PanelListContentAsserter):
    def assert_row_details(self, row, expected_result):
        assert row is not None
        assert expected_result is not None


class TestSpecimenListRequiresLogin(SpecimenListTester, RequiresLoginTester):
    ...


class TestSpecimenIndex(SpecimenListTester, IndexTester):
    @property
    def content_asserter(self) -> RowContentAsserter:
        return SpecimenRowContentAsserter

    @pytest.mark.parametrize("item_count", PagedResultSet.test_page_edges())
    @pytest.mark.parametrize("current_page", PagedResultSet.test_current_pages())
    def test__get__no_filters(self, item_count, current_page):
        phages = self.faker.phage().get_list(save=True, item_count=item_count)

        self.parameters['page'] = current_page

        resp = self.get()

        SpecimenSearchFormTester(
            type_options=dict(get_type_choices()),
            bacterial_species_options=dict(get_bacterial_species_choices()),
        ).assert_all(resp=resp)

        self.assert_all(
            page_count_helper=PagedResultSet(page=current_page, expected_results=phages),
            resp=resp,
        )
