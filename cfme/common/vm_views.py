# -*- coding: utf-8 -*-
from time import sleep

from widgetastic.widget import View, Text, TextInput, Checkbox
from widgetastic_patternfly import (
    Dropdown, BootstrapSelect, FlashMessages, Tab, Input, BootstrapTreeview)

from cfme.base.login import BaseLoggedInPage
from cfme.exceptions import TemplateNotFound
from widgetastic_manageiq import (
    Calendar, SummaryTable, Button, ItemsToolBarViewSelector, Table, MultiBoxSelect,
    CheckableManageIQTree, VersionPick, Version, CheckboxSelect, BaseEntitiesView)


class VMToolbar(View):
    """
    Toolbar view for vms/instances collection destinations
    """
    reload = Button(title='Reload current display')
    configuration = Dropdown('Configuration')
    policy = Dropdown('Policy')
    lifecycle = Dropdown('Lifecycle')
    power = Dropdown('Power Operations')  # title
    download = Dropdown('Download')

    view_selector = View.nested(ItemsToolBarViewSelector)


class VMEntities(BaseEntitiesView):
    """
    Entities view for vms/instances collection destinations
    """
    adv_search_clear = Text('//div[@id="main-content"]//h1//span[@id="clear_search"]/a')


class VMDetailsEntities(View):
    """
    Details entities view for vms/instances details destinations

    VM's have 3-4 more tables, should inherit and add them there.
    """
    title = Text('//div[@id="main-content"]//h1//span[@id="explorer_title_text"]')
    flash = FlashMessages('.//div[@id="flash_msg_div"]'
                          '/div[@id="flash_text_div" or contains(@class, "flash_text_div")]')
    properties = SummaryTable(title='Properties')
    lifecycle = SummaryTable(title='Lifecycle')
    relationships = SummaryTable(title='Relationships')
    vmsafe = SummaryTable(title='VMsafe')
    attributes = SummaryTable(title='Custom Attributes')  # Only displayed when assigned
    compliance = SummaryTable(title='Compliance')
    power_management = SummaryTable(title='Power Management')
    security = SummaryTable(title='Security')
    configuration = SummaryTable(title='Configuration')
    diagnostics = SummaryTable(title='Diagnostics')
    smart_management = SummaryTable(title='Smart Management')


class ProvisionView(BaseLoggedInPage):
    """
    The provisioning view, with nested ProvisioningForm as `form` attribute.
    Handles template selection before Provisioning form with `before_fill` method
    """
    title = Text('#explorer_title_text')

    @View.nested
    class form(View):  # noqa
        """First page of provision form is image selection
        Second page of form is tabbed with nested views
        """
        image_table = Table('//div[@id="pre_prov_div"]//table')
        continue_button = Button('Continue')  # Continue button on 1st page, image selection
        submit_button = Button('Submit')  # Submit for 2nd page, tabular form
        cancel_button = Button('Cancel')

        def before_fill(self, values):
            # Provision from image is a two part form,
            # this completes the image selection before the tabular parent form is filled
            template_name = values.get('template_name',
                                       self.parent_view.context['object'].template_name)
            provider_name = self.parent_view.context['object'].provider.name
            try:
                row = self.image_table.row(name=template_name,
                                           provider=provider_name)
            except IndexError:
                raise TemplateNotFound('Cannot find template "{}" for provider "{}"'
                                       .format(template_name, provider_name))
            row.click()
            self.continue_button.click()
            # TODO timing, wait_displayed is timing out and can't get it to stop in is_displayed
            sleep(3)
            self.flush_widget_cache()

        @View.nested
        class request(Tab):  # noqa
            TAB_NAME = 'Request'
            email = Input(name='requester__owner_email')
            first_name = Input(name='requester__owner_first_name')
            last_name = Input(name='requester__owner_last_name')
            notes = Input(name='requester__request_notes')
            manager_name = Input(name='requester__owner_manager')

        @View.nested
        class purpose(Tab):  # noqa
            TAB_NAME = 'Purpose'
            apply_tags = VersionPick({
                Version.lowest(): CheckboxSelect('//div[@id="all_tags_treebox"]//ul'),
                '5.7': BootstrapTreeview('all_tags_treebox')})

        @View.nested
        class catalog(Tab):  # noqa
            TAB_NAME = 'Catalog'
            num_instances = BootstrapSelect('service__number_of_vms')
            vm_name = Input(name='service__vm_name')
            vm_description = Input(name='service__vm_description')
            vm_filter = BootstrapSelect('service__vm_filter')
            num_vms = BootstrapSelect('service__number_of_vms')
            catalog_name = Table('//div[@id="prov_vm_div"]/table')
            provision_type = BootstrapSelect('service__provision_type')
            linked_clone = Input(name='service__linked_clone')
            pxe_server = BootstrapSelect('service__pxe_server_id')
            pxe_image = Table('//div[@id="prov_pxe_img_div"]/table')
            iso_file = Table('//div[@id="prov_iso_img_div"]/table')

        @View.nested
        class environment(Tab):  # noqa
            TAB_NAME = 'Environment'

            automatic_placement = Checkbox(id='environment__placement_auto')
            # Cloud
            availability_zone = BootstrapSelect('environment__placement_availability_zone')
            cloud_network = BootstrapSelect('environment__cloud_network')
            cloud_subnet = BootstrapSelect('environment__cloud_subnet')
            security_groups = BootstrapSelect('environment__security_groups')
            resource_groups = BootstrapSelect('environment__resource_group')
            public_ip_address = BootstrapSelect('environment__floating_ip_address')
            # Infra
            provider_name = BootstrapSelect('environment__placement_ems_name')
            datacenter = BootstrapSelect('environment__placement_dc_name')
            cluster = BootstrapSelect('environment__placement_cluster_name')
            resource_pool = BootstrapSelect('environment__placement_rp_name')
            folder = BootstrapSelect('environment__placement_folder_name')
            host_filter = BootstrapSelect('environment__host_filter')
            host_name = Table('//div[@id="prov_host_div"]/table')
            datastore_create = Input('environment__new_datastore_create')
            datastore_filter = BootstrapSelect('environment__ds_filter')
            datastore_name = Table('//div[@id="prov_ds_div"]/table')

        @View.nested
        class hardware(Tab):  # noqa
            TAB_NAME = 'Hardware'
            num_sockets = BootstrapSelect('hardware__number_of_sockets')
            cores_per_socket = BootstrapSelect('hardware__cores_per_socket')
            num_cpus = BootstrapSelect('hardware__number_of_cpus')
            memory = BootstrapSelect('hardware__vm_memory')
            # TODO patternfly radio widget, RadioGroup doesn't apply here
            #  disk_format, hardware__disk_format')
            vm_limit_cpu = Input(name='hardware__cpu_limit')
            vm_limit_memory = Input(name='hardware__memory_limit')
            vm_reserve_cpu = Input(name='hardware__cpu_reserve')
            vm_reserve_memory = Input(name='hardware__memory_reserve')

        @View.nested
        class network(Tab):  # noqa
            TAB_NAME = 'Network'
            vlan = BootstrapSelect('network__vlan')

        @View.nested
        class properties(Tab):  # noqa
            TAB_NAME = 'Properties'
            instance_type = BootstrapSelect('hardware__instance_type')
            guest_keypair = BootstrapSelect('hardware__guest_access_key_pair')
            hardware_monitoring = BootstrapSelect('hardware__monitoring')
            boot_disk_size = BootstrapSelect('hardware__boot_disk_size')
            # GCE
            is_preemtible = VersionPick({
                Version.lowest(): None, '5.7': Input(name='hardware__is_preemptible')})

        @View.nested
        class customize(Tab):  # noqa
            TAB_NAME = 'Customize'
            # Common
            dns_servers = Input(name='customize__dns_servers')
            dns_suffixes = Input(name='customize__dns_suffixes')
            customize_type = BootstrapSelect('customize__sysprep_enabled')
            specification_name = Table('//div[@id="prov_vc_div"]/table')
            admin_username = Input(name='customize__root_username')
            admin_password = Input(name='customize__root_password')
            linux_host_name = Input(name='customize__linux_host_name')
            linux_domain_name = Input(name='customize__linux_domain_name')
            ip_address = Input(name='customize__ip_addr')
            subnet_mask = Input(name='customize__subnet_mask')
            gateway = Input(name='customize__gateway')
            custom_template = Table('//div[@id="prov_template_div"]/table')
            hostname = Input(name='customize__hostname')

        @View.nested
        class schedule(Tab):  # noqa
            TAB_NAME = 'Schedule'
            # Common
            # TODO radio widget # schedule_type = Radio('schedule__schedule_type')
            provision_date = Calendar('miq_date_1')
            provision_start_hour = BootstrapSelect('start_hour')
            provision_start_min = BootstrapSelect('start_min')
            power_on = Input(name='schedule__vm_auto_start')
            retirement = BootstrapSelect('schedule__retirement')
            retirement_warning = BootstrapSelect('schedule__retirement_warn')
            # Infra
            stateless = Input(name='schedule__stateless')

    @property
    def is_displayed(self):
        return False


class RetirementView(BaseLoggedInPage):
    """
    Set Retirement date view for vms/instances
    The title actually as Instance|VM.VM_TYPE string in it, otherwise the same
    """

    title = Text('#explorer_title_text')

    @View.nested
    class form(View):  # noqa
        """The form portion of the view"""
        retirement_date = Calendar(name='retirementDate')
        # TODO This is just an anchor with an image, weaksauce
        # remove_date = Button()
        retirement_warning = BootstrapSelect(id='retirementWarning')
        save_button = Button('Save')
        cancel_button = Button('Cancel')

    @property
    def is_displayed(self):
        # TODO match quadicon and title
        return False


class EditView(BaseLoggedInPage):
    """
    Edit vms/instance page
    The title actually as Instance|VM.VM_TYPE string in it, otherwise the same
    """
    title = Text('#explorer_title_text')

    @View.nested
    class form(View):  # noqa
        """The form portion of the view"""
        custom_identifier = TextInput(id='custom_1')
        description = TextInput(id='description')
        parent_vm = BootstrapSelect(id='chosen_parent')
        # MultiBoxSelect element only has table ID in CFME 5.8+
        # https://bugzilla.redhat.com/show_bug.cgi?id=1463265
        chile_vms = MultiBoxSelect(id='child-vm-select')
        save_button = Button('Save')
        reset_button = Button('Reset')
        cancel_button = Button('Cancel')

    @property
    def is_displayed(self):
        # Only name is displayed
        return False


class EditTagsView(BaseLoggedInPage):
    """
    Edit vms/instance tags page
    The title actually as Instance|VM.VM_TYPE string in it, otherwise the same
    """
    @View.nested
    class form(View):  # noqa
        tag_category = BootstrapSelect('tag_cat')
        tag = BootstrapSelect('tag_add')
        # TODO implement table element with ability to remove selected tags
        # https://github.com/RedHatQE/widgetastic.core/issues/26
        save_button = Button('Save')
        reset_button = Button('Reset')
        cancel_button = Button('Cancel')

    @property
    def is_displayed(self):
        # TODO match quadicon
        return False


class SetOwnershipView(BaseLoggedInPage):
    """
    Set vms/instance ownership page
    The title actually as Instance|VM.VM_TYPE string in it, otherwise the same
    """
    @View.nested
    class form(View):  # noqa
        user_name = BootstrapSelect('user_name')
        group_name = BootstrapSelect('group_name')
        save_button = Button('Save')
        reset_button = Button('Reset')
        cancel_button = Button('Cancel')

    @property
    def is_displayed(self):
        # TODO match quadicon
        return False


class ManagementEngineView(BaseLoggedInPage):
    """
    Edit management engine relationship page
    The title actually as Instance|VM.VM_TYPE string in it, otherwise the same
    """
    @View.nested
    class form(View):  # noqa
        server = BootstrapSelect('server_id')
        save_button = Button('Save')
        reset_button = Button('Reset')
        cancel_button = Button('Cancel')

    @property
    def is_displayed(self):
        # Only the name is displayed
        return False


class ManagePoliciesView(BaseLoggedInPage):
    """
    Manage policies page
    """
    @View.nested
    class form(View):  # noqa
        policy_profiles = CheckableManageIQTree(tree_id='protectbox')
        save_button = Button('Save')
        reset_button = Button('Reset')
        cancel_button = Button('Cancel')

    @property
    def is_displayed(self):
        # TODO match quadicon
        return False


class PolicySimulationView(BaseLoggedInPage):
    """
    Policy Simulation page for vms/instances
    """
    @View.nested
    class form(View):  # noqa
        policy = BootstrapSelect('policy_id')
        # TODO policies table, ability to remove
        cancel_button = Button('Cancel')

    @property
    def is_displayed(self):
        # TODO match quadicon
        return False


class RightSizeView(BaseLoggedInPage):
    """
    Right Size recommendations page for vms/instances
    """
    # TODO new table widget for right-size tables
    # They're H3 headers with the table as following-sibling

    @property
    def is_displayed(self):
        # Only name is displayed
        return False
