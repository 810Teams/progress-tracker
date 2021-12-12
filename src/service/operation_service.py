"""
    `operations.py`
"""

from custom.append import custom_append_head
from src.model.operation import Operation
from src.core.app_data import OPERATION_LIST, SUPPORTED_STYLES
from src.model.command import Command
from src.model.storage import Storage
from src.service.render_service import RenderService
from src.util.logging import error, notice
from src.util.reader import convert_csv_to_list
from settings import DEFAULT_STYLE


class OperationService:
    def __init__(self, storage: Storage) -> None:
        self.storage = storage
        self.render_service = RenderService(storage)


    def execute(self, command: Command) -> None:
        if not self.validate_command(command):
            error('Command \'{}\' error.'.format(command.name), start='\n')
        else:
            exec('self.operate_{}(command)'.format(command.name))


    def operate_append(self, command: Command) -> None:
        """ Function: Operation Code 'A' (Add Data) """
        value = command.value

        if command.contains_argument('--add'):
            try:
                value = convert_csv_to_list(value, value_type=int, replace_null=0)
                initial = self.storage.to_list()[-1][1:]

                new_row = [int(initial[i]) + value[i] for i in range(len(initial))]
                self.storage.append(new_row)
                notice('Data {} is added to the storage.'.format(new_row), start='\n')
            except ValueError:
                error('Invalid value format. Please try again.', start='\n')

        elif command.contains_argument('-custom'):
            try:
                custom_id = int(command.get_argument('-custom').value)
                if custom_id not in (1, 2, 3, 4, 5):
                    error('Custom ID must be an integer from 1 to 5.', start='\n')
                    return
            except (IndexError, ValueError):
                error('Custom ID must be an integer.', start='\n')
                return

            try:
                new_row = custom_append_head(value, custom_id)
                self.storage.append(new_row)
                notice('Data {} is added to the storage.'.format(new_row), start='\n')
            except IndexError:
                error('Invalid value format. Please try again.', start='\n')
                error('Function \'custom_append_{}\' might not have been implemented.'.format(custom_id))

        else:
            try:
                new_row = convert_csv_to_list(value, value_type=int, replace_null=0)
                self.storage.append(new_row)
                notice('Data {} is added to the storage.'.format(new_row), start='\n')
            except ValueError:
                error('Invalid value format. Please try again.', start='\n')


    def operate_chart(self, command: Command) -> None:
        """ Function: Operation Code 'C' (Create Charts) """
        # Step 1: -average argument
        average_range = None
        if command.contains_argument('-average-range'):
            # Test for valid format
            try:
                average_range = int(command.get_argument('-average-range').value)
            except (IndexError, ValueError):
                error('Average range must be an integer.', start='\n')
                error('Aborting chart creation process.')
                return

        # Step 2: -days argument
        days = 0
        if command.contains_argument('-days'):
            # Test for valid format
            try:
                days = int(command.get_argument('-days').value)
            except (IndexError, ValueError):
                error('Duration must be an integer.', start='\n')
                error('Aborting chart creation process.')
                return

        # Step 3: -max-dots argument
        dots_count = 100
        if command.contains_argument('-dots-count'):
            try:
                dots_count = int(command.get_argument('-dots-count').value)
            except (IndexError, ValueError):
                error('Maximum dots must be an integer.', start='\n')
                error('Aborting chart creation process.')
                return

        # Step 4: -max-y argument
        max_y_labels = 15
        if command.contains_argument('-max-y'):
            # Step 4.1 - Test for valid format
            try:
                max_y_labels = int(command.get_argument('-max-y').value)
            except (IndexError, ValueError):
                error('Maximum y labels must be an integer.', start='\n')
                error('Aborting chart creation process.')
                return

            # Step 4.2 - Test for valid requirements
            if not (max_y_labels >= 2):
                error('Maximum y labels must be an integer at least 2.', start='\n')
                error('Aborting chart creation process.')
                return

        # Step 5: -style argument
        style = 'DefaultStyle'
        if command.contains_argument('-style'):
            # Step 5.1.1 - Test for valid format
            try:
                style = command.get_argument('-style').value
            except (IndexError, ValueError):
                error('Invalid style.', start='\n')
                error('Aborting chart creation process.')
                return

            # Step 5.1.2 - Test for valid requirements
            if style not in SUPPORTED_STYLES:
                error('Invalid style.', start='\n')
                error('Aborting chart creation process.')
                return
        elif DEFAULT_STYLE:
            style = DEFAULT_STYLE

            # Step 4.2.1 - Test for valid requirements
            if DEFAULT_STYLE not in SUPPORTED_STYLES:
                error('Invalid style found in \'settings.py\'.', start='\n')
                error('Aborting chart creation process.')
                return

            notice('Default style is found in \'settings.py\', now proceeding to chart creation.', start='\n')
            notice('Style \'{}\' will be used in chart creation.'.format(DEFAULT_STYLE))

        # Step 6: -x-label argument
        x_label = 'date'
        if command.contains_argument('-x-label'):
            # Step 6.1 - Test for valid format
            try:
                x_label = command.get_argument('-x-label').value
            except (IndexError, ValueError):
                error('X-label type must be a string.', start='\n')
                error('Aborting chart creation process.')
                return

            # Step 6.2 - Test for valid requirements
            if x_label not in ('date', 'count', 'both'):
                error('X-label type must be either \'date\', \'count\', or \'both\'', start='\n')
                error('Aborting chart creation process.')
                return

        # Step 7: Render charts
        self.render_service.render_all(
            allow_float=command.contains_argument('--allow-float'),
            average_range=average_range,
            days=days,
            is_dynamic=command.contains_argument('--dynamic'),
            is_today=command.contains_argument('--today'),
            dots_count=dots_count,
            max_y_labels=max_y_labels,
            style=style,
            x_label=x_label
        )


    def operate_reload(self, command: Command) -> None:
        """ Function: Operation Code 'R' (Reload Storage) """
        self.storage.reload()
        notice('Storage \'{}\' is reloaded from disk.'.format(self.storage.name), start='\n')


    def operate_save(self, command: Command) -> None:
        """ Function: Operation Code 'S' (Save Storage) """
        self.storage.save()


    def operate_view(self, command: Command) -> None:
        """ Function: Operation Code 'V' (View Storage) """
        print()
        print(self.storage.data)


    def operate_exit(self, command: Command) -> None:
        """ Function: Operation Code 'X' (Exit) """
        notice('Exitting application.', start='\n')
        exit()


    def validate_command(self, command: Command) -> bool:
        operation = self.find_operation(command)

        if operation is None:
            return False

        return operation.validate_command(command)


    def find_operation(self, command: Command) -> Operation:
        operation: Operation
        for operation in OPERATION_LIST:
            if command.name == operation.name:
                return operation
        return None
