"""
a way to generate uservars from pymtpl

"""

from gadget.pylog import log
from gadget.errors import confirm, ErrorUser, ErrorInput, Check
from gadget.files import File
from gadget.disk import mkdirs
from gadget.helperclass import OPT, IS_UT, NoneLikeClass
from gadget.gizmo import get_caller_lno


class UserVars:
    """Used to create a uservars collection.

    :param filename: Name of the uservar file to create (without .usrv extension)
    :type filename: str
    :param setname: Name of the uservar set. If None, uses the filename as the setname.
    :type setname: str or None

    Features:
        - Allows adding variables as attributes to the UserVars object.
        - Variables can be used directly in parameters, eg. myparam = usrv.MyVar
        - Supports variable types: Integer, Double, String, Boolean, and their array forms.
        - Supports adding variables as Spec references for complex expressions (requires tuple input).
        - Infers variable types from the value provided when possible.
        - Mouseover shows simple variable values when using Visual Studio

    Usage::

        usrv = UserVars('PTH_DTS')
        usrv.MyInt = 20
        usrv.MyDouble = -99.0
        usrv.MyString = "Hello"
        usrv.MyBool = True
        usrv.MyIntArray = [1, 2, 3, 4, 5]
        usrv.MySpecDouble = ("SomeComplexExpression()", float)
        usrv.MySpecStringArray = ('[Expression(), "Hello", "World"]', [str])

        test = MyTestCase(
            TestParameter = usrv.MyString,
        )

    Uservar File Output in PTH_DTS.usrv::

        Version 1.0;
        UserVars PTH_DTS
        {
            Integer MyInt = 20;
            Double MyDouble = -99.0;
            String MyString = "Hello";
            Boolean MyBool = True;
            Integer[] MyIntArray = [1,2,3,4,5];
            Double MySpecDouble = SomeComplexExpression();
            String[] MySpecStringArray = [Expression(),"Hello","World"];
        }

    """

    _uservar_registry = []

    def __init__(self,
                 filename,               # name of the uservar filename
                 setname=None,               # name of the uservar set
                 ):
        """Initialize a UserVars instance.

        :param filename: Name of the uservar file to create (without .usrv extension)
        :param setname: Name of the uservar set. If None, uses filename as the setname
        :raises ErrorUser: If a UserVars set with the same setname already exists
        """
        from pymtpl.core import Import  # avoids circular dependency
        id_lno = get_caller_lno()
        # validate filename
        validated_filename = Check.is_str('filename', filename, lno=id_lno)
        self._filename = validated_filename
        # validate setname
        if setname is None:
            setname = validated_filename
        validated_setname = Check.is_str('setname', setname, lno=id_lno)
        self._setname = validated_setname
        # initialize variables collection
        self._variables = []
        # add this file to the import registry so it gets imported
        uservar_full_path = f'{validated_filename}.usrv'
        if uservar_full_path not in Import._import_registry_name:
            Import._import_registry_name.append(f'{validated_filename}.usrv')
        # Add this uservar set to the global registry so the uservar file gets generated
        confirm(validated_setname not in [uv._setname for uv in UserVars._uservar_registry],
                f'A UserVars set with the name {validated_setname} already exists. Please choose a different name.',
                f'Please check line# {id_lno}')
        UserVars._uservar_registry.append(self)

    @classmethod
    def clear_registry(cls):
        """Clear the global UserVars registry.

        Used primarily in unit tests to reset state between test cases.
        """
        cls._uservar_registry.clear()

    def __getattribute__(self, name):
        """Custom attribute access handler.

        Returns methods and internal attributes (starting with _) normally.
        For other attributes, returns a Spec reference if the attribute is a registered uservar.

        :param name: The attribute name being accessed
        :return: For methods: The callable method object
                 For internal attributes: The attribute value
                 For uservars: A Spec object representing the uservar reference
        :raises ErrorUser: If the attribute is not found in registered uservars
        """
        # Allow access to internal attributes that start with underscore
        if name.startswith('_'):
            return super().__getattribute__(name)

        id_lno = get_caller_lno()
        # Get setname first so it's available in both try and except blocks
        setname = super().__getattribute__('_setname')

        # Try to get the attribute normally first
        try:
            attr = super().__getattribute__(name)
            # If it's callable (a method), return it normally
            if callable(attr):
                return attr
        except AttributeError:
            pass
        confirm(name in [var[1] for var in self._variables],
                f'UserVar "{name}" not found in UserVars set "{setname}".', f'Please check line# {id_lno}')
        # If attribute doesn't exist, return a Spec reference (user is accessing a uservar)
        from pymtpl.core import Spec  # avoids circular dependency
        return Spec(f"{setname}.{name}")

    def __setattr__(self, name, value):
        """Adds a variable to the uservars collection.

        Supports various value types and automatically infers the uservar type.

        :param name: The variable name (must not start with _)
        :param value: Variable value. Supported types:
                      - Simple values: int, float, str, bool
                      - Arrays: list of same-type values
                      - Spec expressions: tuple of (expression_string, type) or (expression_string, [type])

        Examples:
            usrv.MyInt = 25
            usrv.MyArray = [1, 2, 3]
            usrv.MySpec = ('SomeExpression()', float)
            usrv.MyArraySpec = ('[1, 2, Expression()]', [int])

        :raises ErrorUser: If value is None, arrays are empty, or array elements have mixed types
        :raises TypeError: If tuple has invalid format or unsupported type is used
        """
        # Allow normal attribute setting for internal attributes (those starting with _)
        if name.startswith('_'):
            super().__setattr__(name, value)
            return

        # get the line number
        id_lno = get_caller_lno()

        # handle variable name
        var_name = Check.is_str('var_name', name, lno=id_lno)
        confirm(value is not None, 'Value is required when adding to uservars',
                f'Please specify a value to use in line# {id_lno}')

        # setup
        is_array_vartype = False
        is_spec = False

        # handling for tuple input (expression, type) - always a Spec for a tuple!
        if isinstance(value, tuple):
            confirm(len(value) == 2, 'When adding a uservar with a tuple, it must be of length 2', f'Please check line# {id_lno}. Expecting ("expression", type)')
            confirm(isinstance(value[0], str), 'When adding a uservar with a tuple, the first element must be a string', f'Please check line# {id_lno}. Expecting ("expression", type)')
            value, var_type = value
            is_spec = True
        else:
            var_type = None

        # handle variable type
        if var_type is not None:  # type was specified
            if isinstance(var_type, list):
                confirm(len(var_type) == 1 and isinstance(var_type[0], type), 'When adding a uservar with a tuple and an array type, it must be [type] with length of 1', f'Please check line# {id_lno}. Expecting ("expression", [type])')
                is_array_vartype = True
                var_type = UserVars._infer_var_type_from_type(var_type[0])
            elif isinstance(var_type, type):
                var_type = UserVars._infer_var_type_from_type(var_type)
            else:
                raise TypeError(f'When adding a uservar with a tuple, the second element must be a type or [type]. Please check line# {id_lno}.')
        elif isinstance(value, list):  # infer type from list value
            is_array_vartype = True
            # infer type from first element of the list
            confirm(len(value) > 0, 'When adding a uservar with an array value, the array cannot be empty', f'Please check line# {id_lno}.')
            # confirm all elements are the same type
            var_type = UserVars._infer_var_type_from_type(type(value[0]))
            for v in value:
                confirm(UserVars._infer_var_type_from_type(type(v)) == var_type,
                        'When adding a uservar with an array value, all elements in the array must be of the same type',
                        f'Please check line# {id_lno}.')
        else:  # infer type from single value
            var_type = UserVars._infer_var_type_from_type(type(value))
        self._variables.append((var_type, var_name, value, is_spec, is_array_vartype))

    @classmethod
    def _infer_var_type_from_type(cls, var_type):
        """Convert Python type to uservar type string.

        :param var_type: Python type (int, float, str, or bool)
        :return: String representation: 'Integer', 'Double', 'String', or 'Boolean'
        :raises TypeError: If var_type is not int, float, str, or bool
        """
        id_lno = get_caller_lno()
        is_array_vartype = False
        if var_type == int:
            return 'Integer'
        elif var_type == float:
            return 'Double'
        elif var_type == str:
            return 'String'
        elif var_type == bool:
            return 'Boolean'
        else:
            raise TypeError(f'When adding a uservar with a type, the type must be int, float, str, or bool. Please check line# {id_lno}.')

    @classmethod
    def write_all_uservars(cls, module_name):
        """Write all registered UserVars to .usrv files.

        Groups UserVars by filename and writes each group to a separate .usrv file.
        Empty UserVars sets are skipped. If file content hasn't changed, the file
        is not rewritten (logs "NO UPDATE" message).

        :param module_name: Name of the module (used for validation)

        Note:
            Multiple UserVars with the same filename will be written to the same .usrv file
            as separate UserVars sets.
        """
        id_lno = get_caller_lno()
        module_name = Check.is_str('module_name', module_name, lno=id_lno)

        # Group uservar sets by filename
        filename_groups = {}
        for uservar_set in cls._uservar_registry:
            filename = uservar_set._filename
            if filename not in filename_groups:
                filename_groups[filename] = []
            filename_groups[filename].append(uservar_set)

        # Write a separate file for each unique filename
        for filename, uservar_sets in filename_groups.items():
            uservar_file_lines = cls._get_uservars_lines_for_file(uservar_sets)
            if len(uservar_file_lines) == 0:
                continue  # skip writing empty uservar files
            uservars_file_path = f'{filename}.usrv'
            if not File(uservars_file_path).rewrite('\n'.join(uservar_file_lines), 'pymtpl.uservars.write_all_uservars()'):
                log.info(f'-i- NO UPDATE: No changes to {uservars_file_path}')

    @classmethod
    def _get_uservars_lines_for_file(cls, uservar_sets):
        """Generate file content lines for UserVars sets sharing the same file.

        :param uservar_sets: List of UserVars instances to write to the same file
        :return: List of strings representing the complete file content, or empty list if
                 all uservar sets are empty

        Note:
            Skips empty uservar sets. Returns empty list if no variables to write.
        """
        uservar_file_lines = []
        uservar_file_lines.append('Version 1.0;')
        for uservar_set in uservar_sets:
            if len(uservar_set._variables) == 0:
                continue  # skip empty uservar sets
            uservar_file_lines.append('')  # blank line between sets
            uservar_file_lines.append(f'UserVars {uservar_set._setname.strip()}')
            uservar_file_lines.append('{')
            for line in uservar_set._write_variables():
                uservar_file_lines.append(line)
            uservar_file_lines.append('}')
        if len(uservar_file_lines) == 1:
            return []  # no uservars to write
        return uservar_file_lines

    def _write_variables(self):
        """Generate formatted output lines for each variable in the collection.

        :return: Formatted string for each variable in the proper .usrv file syntax.
                 Format varies based on variable type (simple, array, spec, string).

        Note:
            - Strings are wrapped in double quotes (unless they are spec expressions)
            - Arrays use Array<Type> syntax
            - All whitespace in values is removed
        """
        for var_type, var_name, value, is_spec, is_array_vartype in self._variables:
            value = str(value).replace(' ', '')  # remove spaces
            if is_array_vartype:
                array_var = f'Array<{var_type}>'
                # Format array values properly with double quotes for strings
                if var_type.lower() == 'string':
                    value = value.replace("'", '"')  # ensure double quotes
                yield f'    {array_var} {var_name} = {value};'
            elif var_type.lower() == 'string' and not is_spec:
                yield f'    {var_type} {var_name} = "{value}";'
            else:
                yield f'    {var_type} {var_name} = {value};'
