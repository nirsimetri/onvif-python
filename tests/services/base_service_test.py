# tests/services/base_service_test.py

import os
import inspect
import ast
from unittest.mock import Mock, patch
from lxml import etree
from typing import Dict, List, Any, Optional, Type


class ONVIFServiceTestBase:
    """Base class for ONVIF service testing to reduce code duplication."""

    # These should be overridden in subclasses
    SERVICE_CLASS: Optional[Type] = None
    SERVICE_NAME: str = ""
    WSDL_PATH_COMPONENTS: List[str] = (
        []
    )  # e.g., ["ver10", "device", "wsdl", "devicemgmt.wsdl"]
    BINDING_NAME: str = ""  # e.g., "DeviceBinding"
    NAMESPACE_PREFIX: str = ""  # e.g., "tds"
    SERVICE_NAMESPACE: str = ""  # e.g., "http://www.onvif.org/ver10/device/wsdl"
    XADDR_PATH: str = ""  # e.g., "/onvif/device_service"

    @classmethod
    def get_wsdl_operations(cls) -> Dict[str, Dict[str, List[str]]]:
        """Parse WSDL to get all defined operations with their parameters."""
        if not cls.WSDL_PATH_COMPONENTS:
            return {}

        wsdl_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            "onvif",
            "wsdl",
            *cls.WSDL_PATH_COMPONENTS,
        )

        if not os.path.exists(wsdl_path):
            return {}

        # Parse WSDL
        tree = etree.parse(wsdl_path)
        root = tree.getroot()

        # Namespaces
        ns = {
            "wsdl": "http://schemas.xmlsoap.org/wsdl/",
            "xs": "http://www.w3.org/2001/XMLSchema",
            cls.NAMESPACE_PREFIX: cls.SERVICE_NAMESPACE,
        }

        operations = {}

        # Find all operations in binding instead of portType
        binding = root.find(f'.//wsdl:binding[@name="{cls.BINDING_NAME}"]', ns)
        if binding is not None:
            for operation in binding.findall("wsdl:operation", ns):
                op_name = operation.get("name")

                # Look for the element definition for this operation
                element = root.find(f'.//xs:element[@name="{op_name}"]', ns)
                params = []
                if element is not None:
                    # Look for sequence elements within the complexType
                    sequence = element.find(".//xs:sequence", ns)
                    if sequence is not None:
                        for elem in sequence.findall("xs:element", ns):
                            param_name = elem.get("name")
                            if param_name:
                                params.append(param_name)

                operations[op_name] = {
                    "request_params": params,
                    "response_params": [],  # We don't need response params for this test
                }

        return operations

    @classmethod
    def get_implemented_methods(cls) -> Dict[str, Dict[str, Any]]:
        """Get all implemented methods in service class."""
        if not cls.SERVICE_CLASS:
            return {}

        methods = {}
        for name, method in inspect.getmembers(
            cls.SERVICE_CLASS, predicate=inspect.isfunction
        ):
            if not name.startswith("_") and name != "__init__":
                # Get method signature
                sig = inspect.signature(method)
                params = list(sig.parameters.keys())
                # Remove 'self' from parameters
                if "self" in params:
                    params.remove("self")

                methods[name] = {
                    "params": params,
                    "signature": sig,
                }

        return methods

    def test_import(self):
        """Test that service class can be imported."""
        assert self.SERVICE_CLASS is not None

    def test_no_duplicate_methods(self):
        """Test that there are no duplicate method implementations in service class."""
        if not self.SERVICE_CLASS:
            return

        # Get the source file of the service class
        source_file = inspect.getsourcefile(self.SERVICE_CLASS)
        if not source_file:
            return

        # Parse the source file
        with open(source_file, "r", encoding="utf-8") as f:
            source_code = f.read()

        tree = ast.parse(source_code)

        # Find the class definition
        class_node = None
        for node in ast.walk(tree):
            if (
                isinstance(node, ast.ClassDef)
                and node.name == self.SERVICE_CLASS.__name__
            ):
                class_node = node
                break

        if not class_node:
            return

        # Collect all method names defined in the class
        method_names = []
        method_line_numbers = {}

        for item in class_node.body:
            if isinstance(item, ast.FunctionDef):
                method_name = item.name
                # Skip private methods and __init__
                if method_name.startswith("_") or method_name == "__init__":
                    continue

                # Skip helper methods
                if method_name in ["type", "desc", "operations"]:
                    continue

                method_names.append(method_name)

                # Track line numbers for better error reporting
                if method_name not in method_line_numbers:
                    method_line_numbers[method_name] = []
                method_line_numbers[method_name].append(item.lineno)

        # Find duplicates
        from collections import Counter

        method_counts = Counter(method_names)
        duplicates = [
            f"{name}: defined {count} times at lines {method_line_numbers[name]}"
            for name, count in method_counts.items()
            if count > 1
        ]

        assert not duplicates, (
            f"Duplicate method implementations found in {self.SERVICE_CLASS.__name__}:\n"
            + "\n".join(duplicates)
        )

    def test_wsdl_operations_not_empty(self):
        """Test that WSDL operations are successfully parsed and not empty."""
        wsdl_operations = self.get_wsdl_operations()

        assert wsdl_operations, (
            f"No WSDL operations found. Check if:\n"
            f"1. WSDL file exists at: {self.WSDL_PATH_COMPONENTS}\n"
            f"2. BINDING_NAME '{self.BINDING_NAME}' is correct\n"
            f"3. NAMESPACE_PREFIX '{self.NAMESPACE_PREFIX}' and SERVICE_NAMESPACE '{self.SERVICE_NAMESPACE}' are correct\n"
            f"4. WSDL parsing is working correctly"
        )

        # Also check that operations have meaningful content
        operations_with_params = 0
        for op_name, op_info in wsdl_operations.items():
            assert isinstance(
                op_info, dict
            ), f"Operation {op_name} should have dict info"
            assert (
                "request_params" in op_info
            ), f"Operation {op_name} should have request_params"
            if op_info["request_params"]:
                operations_with_params += 1

        # Log some useful information
        print(f"\nParsed {len(wsdl_operations)} operations from WSDL")
        print(f"Operations with parameters: {operations_with_params}")
        print(f"Operations found: {list(wsdl_operations.keys())}")

    def test_all_wsdl_operations_implemented(self):
        """Test that all WSDL operations are implemented as methods."""
        wsdl_operations = self.get_wsdl_operations()
        implemented_methods = self.get_implemented_methods()

        missing_operations = []
        for op_name in wsdl_operations.keys():
            if op_name not in implemented_methods:
                missing_operations.append(op_name)

        assert (
            not missing_operations
        ), f"Missing implementations for operations: {missing_operations}"

    def test_method_parameters_match_wsdl(self):
        """Test that method parameters match WSDL request parameters."""
        wsdl_operations = self.get_wsdl_operations()
        implemented_methods = self.get_implemented_methods()

        # Known parameter name corrections that we want to catch
        known_issues = []

        for op_name, op_info in wsdl_operations.items():
            if op_name not in implemented_methods:
                continue

            method_info = implemented_methods[op_name]
            method_params = set(method_info["params"])
            wsdl_params = set(op_info["request_params"])

            # Skip empty parameter cases (methods without parameters are OK)
            if not wsdl_params and not method_params:
                continue

            # Check for method parameters that don't have exact match in WSDL
            # but are similar to WSDL parameters (potential typos)
            for method_param in method_params:
                if method_param not in wsdl_params:
                    # This method parameter doesn't exist in WSDL
                    # Look for similar WSDL parameters that might be the correct name
                    for wsdl_param in wsdl_params:
                        # Check for obvious typos using similarity heuristics
                        if self._is_likely_typo(method_param, wsdl_param):
                            known_issues.append(
                                {
                                    "operation": op_name,
                                    "method_param": method_param,
                                    "expected_wsdl_param": wsdl_param,
                                    "issue": "Potential parameter name typo",
                                }
                            )
                            break  # Only report the first likely match

        # Assert that there are no obvious parameter name issues
        if known_issues:
            error_msg = "Parameter name issues found:\n" + "\n".join(
                [
                    f"  {issue['operation']}: '{issue['method_param']}' should be '{issue['expected_wsdl_param']}' ({issue['issue']})"
                    for issue in known_issues
                ]
            )
            assert False, error_msg

    def _is_likely_typo(self, method_param: str, wsdl_param: str) -> bool:
        """Check if method_param is likely a typo of wsdl_param."""
        # Must be different
        if method_param == wsdl_param:
            return False

        # Check for common typo patterns
        method_lower = method_param.lower()
        wsdl_lower = wsdl_param.lower()

        # Pattern 1: Missing characters at the end (like InterfaceToke vs InterfaceToken)
        if (
            len(method_param) < len(wsdl_param)
            and wsdl_lower.startswith(method_lower)
            and len(wsdl_param) - len(method_param) <= 3
        ):
            return True

        # Pattern 2: Extra characters at the end
        if (
            len(method_param) > len(wsdl_param)
            and method_lower.startswith(wsdl_lower)
            and len(method_param) - len(wsdl_param) <= 3
        ):
            return True

        # Pattern 3: Single character difference in the middle/end
        if abs(len(method_param) - len(wsdl_param)) <= 1:
            # Simple edit distance check for single character changes
            if self._edit_distance(method_lower, wsdl_lower) <= 1:
                return True

        return False

    def _edit_distance(self, s1: str, s2: str) -> int:
        """Calculate simple edit distance (Levenshtein distance)."""
        if len(s1) < len(s2):
            return self._edit_distance(s2, s1)

        if len(s2) == 0:
            return len(s1)

        previous_row = list(range(len(s2) + 1))
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row

        return previous_row[-1]

    def test_operator_call_usage(self):
        """Test that all methods correctly call self.operator.call()."""
        if not self.SERVICE_CLASS:
            return

        with patch(
            f"onvif.services.{self.SERVICE_NAME.lower()}.ONVIFOperator"
        ) as mock_operator_class:
            # Create mock operator
            mock_operator_instance = Mock()
            mock_operator_class.return_value = mock_operator_instance

            # Create service instance
            if not self.SERVICE_CLASS or not callable(self.SERVICE_CLASS):
                raise TypeError(
                    f"SERVICE_CLASS must be a callable class, got {type(self.SERVICE_CLASS)}"
                )
            service = self.SERVICE_CLASS(xaddr=f"http://test:80{self.XADDR_PATH}")

            implemented_methods = self.get_implemented_methods()

            # Skip helper methods that don't call operator.call()
            helper_methods = ["type", "desc", "operations"]

            errors = []

            for method_name, method_info in implemented_methods.items():
                # Skip helper methods
                if method_name in helper_methods:
                    continue

                # Reset mock
                mock_operator_instance.call.reset_mock()

                try:
                    # Get the method
                    method = getattr(service, method_name)

                    # Create dummy arguments based on signature
                    sig = method_info["signature"]
                    kwargs = {}
                    for param_name, param in sig.parameters.items():
                        if param_name == "self":
                            continue
                        # Provide None for optional params, empty string for required
                        if param.default == inspect.Parameter.empty:
                            kwargs[param_name] = ""
                        else:
                            kwargs[param_name] = None

                    # Call the method
                    try:
                        method(**kwargs)
                    except Exception:
                        pass  # We expect it might fail, we just want to check the call

                    # Verify operator.call was invoked
                    if not mock_operator_instance.call.called:
                        errors.append(f"{method_name}: operator.call() not invoked")
                    else:
                        # Check that first argument is the operation name
                        call_args = mock_operator_instance.call.call_args
                        if call_args and len(call_args[0]) > 0:
                            called_op_name = call_args[0][0]
                            if called_op_name != method_name:
                                errors.append(
                                    f"{method_name}: calls operator.call('{called_op_name}') instead of '{method_name}'"
                                )
                        else:
                            errors.append(
                                f"{method_name}: operator.call() called without operation name"
                            )

                except Exception as e:
                    errors.append(f"{method_name}: Error during test - {str(e)}")

            assert not errors, "Operator call errors:\n" + "\n".join(errors)

    def test_no_extra_methods(self):
        """Test that there are no extra public methods not in WSDL."""
        wsdl_operations = self.get_wsdl_operations()
        implemented_methods = self.get_implemented_methods()

        # Allowed helper methods that are not ONVIF operations
        allowed_helper_methods = ["type", "desc", "operations"]

        extra_methods = []
        for method_name in implemented_methods.keys():
            if (
                method_name not in wsdl_operations
                and method_name not in allowed_helper_methods
            ):
                extra_methods.append(method_name)

        # Assert that there are no extra methods
        assert (
            not extra_methods
        ), f"Extra methods found that are not in WSDL: {extra_methods}"

    def test_parameter_forwarding_for_all_methods(self):
        """Test that all method parameters are correctly forwarded to operator.call()."""
        if not self.SERVICE_CLASS:
            return

        with patch(
            f"onvif.services.{self.SERVICE_NAME.lower()}.ONVIFOperator"
        ) as mock_operator_class:
            mock_operator_instance = Mock()
            mock_operator_class.return_value = mock_operator_instance
            mock_operator_instance.call.return_value = {}

            if not self.SERVICE_CLASS or not callable(self.SERVICE_CLASS):
                raise TypeError(
                    f"SERVICE_CLASS must be a callable class, got {type(self.SERVICE_CLASS)}"
                )
            service = self.SERVICE_CLASS(xaddr=f"http://test:80{self.XADDR_PATH}")
            implemented_methods = self.get_implemented_methods()

            # Skip helper methods that don't call operator.call()
            helper_methods = ["type", "desc", "operations"]

            errors = []

            for method_name, method_info in implemented_methods.items():
                # Skip helper methods
                if method_name in helper_methods:
                    continue

                mock_operator_instance.call.reset_mock()

                try:
                    # Get the method
                    method = getattr(service, method_name)

                    # Create test arguments for all parameters
                    sig = method_info["signature"]
                    kwargs = {}
                    for param_name, param in sig.parameters.items():
                        if param_name == "self":
                            continue
                        # Use unique test values to verify parameter names
                        kwargs[param_name] = f"test_{param_name}_value"

                    # Call the method if it has parameters
                    if kwargs:
                        try:
                            method(**kwargs)
                        except Exception:
                            pass  # We expect it might fail, we just want to check the call

                        # Verify operator.call was invoked and parameters forwarded correctly
                        if mock_operator_instance.call.called:
                            call_args = mock_operator_instance.call.call_args
                            if call_args and len(call_args) > 1:
                                called_kwargs = call_args[1]

                                # Check that all method parameters are forwarded correctly
                                for param_name, param_value in kwargs.items():
                                    if param_name not in called_kwargs:
                                        errors.append(
                                            f"{method_name}: parameter '{param_name}' not forwarded to operator.call()"
                                        )
                                    elif called_kwargs[param_name] != param_value:
                                        errors.append(
                                            f"{method_name}: parameter '{param_name}' value mismatch. "
                                            f"Expected: {param_value}, Got: {called_kwargs[param_name]}"
                                        )

                                # Check for typos in parameter names
                                for called_param in called_kwargs.keys():
                                    if called_param not in kwargs:
                                        # Look for similar parameter names that might be typos
                                        for correct_param in kwargs.keys():
                                            if self._is_likely_typo(
                                                called_param, correct_param
                                            ):
                                                errors.append(
                                                    f"{method_name}: parameter name typo in operator.call(). "
                                                    f"Used '{called_param}' but should be '{correct_param}'"
                                                )
                                                break

                except Exception as e:
                    errors.append(
                        f"{method_name}: Error during parameter forwarding test - {str(e)}"
                    )

            assert not errors, "Parameter forwarding errors:\n" + "\n".join(errors)

    def run_parameter_forwarding_tests(self, test_cases: List[Dict[str, Any]]):
        """Test that parameters are correctly forwarded to operator.call()."""
        if not self.SERVICE_CLASS or not test_cases:
            return

        with patch(
            f"onvif.services.{self.SERVICE_NAME.lower()}.ONVIFOperator"
        ) as mock_operator_class:
            mock_operator_instance = Mock()
            mock_operator_class.return_value = mock_operator_instance
            mock_operator_instance.call.return_value = {}

            if not self.SERVICE_CLASS or not callable(self.SERVICE_CLASS):
                raise TypeError(
                    f"SERVICE_CLASS must be a callable class, got {type(self.SERVICE_CLASS)}"
                )
            service = self.SERVICE_CLASS(xaddr=f"http://test:80{self.XADDR_PATH}")

            for test_case in test_cases:
                mock_operator_instance.call.reset_mock()
                method = getattr(service, test_case["method"])
                method(**test_case["params"])

                # Verify call was made with correct parameters
                mock_operator_instance.call.assert_called_once()
                actual_call = mock_operator_instance.call.call_args

                # Check operation name
                assert (
                    actual_call[0][0] == test_case["method"]
                ), f"Operation name mismatch for {test_case['method']}"

                # Check all parameters are forwarded
                for param_name, param_value in test_case["params"].items():
                    assert (
                        param_name in actual_call[1]
                    ), f"Parameter {param_name} not forwarded in {test_case['method']}"
                    assert (
                        actual_call[1][param_name] == param_value
                    ), f"Parameter {param_name} value mismatch in {test_case['method']}"

    def run_specific_methods_tests(self, test_cases: List[Dict[str, Any]]):
        """Test specific important methods are correctly implemented."""
        if not self.SERVICE_CLASS or not test_cases:
            return

        with patch(
            f"onvif.services.{self.SERVICE_NAME.lower()}.ONVIFOperator"
        ) as mock_operator_class:
            mock_operator_instance = Mock()
            mock_operator_class.return_value = mock_operator_instance
            mock_operator_instance.call.return_value = {"Result": "Success"}

            if not self.SERVICE_CLASS or not callable(self.SERVICE_CLASS):
                raise TypeError(
                    f"SERVICE_CLASS must be a callable class, got {type(self.SERVICE_CLASS)}"
                )
            service = self.SERVICE_CLASS(xaddr=f"http://test:80{self.XADDR_PATH}")

            for i, test_case in enumerate(test_cases):
                if i > 0:  # Reset mock for subsequent tests
                    mock_operator_instance.call.reset_mock()

                method = getattr(service, test_case["method"])
                method(**test_case.get("params", {}))

                expected_call_args = [test_case["method"]]
                expected_call_kwargs = test_case.get("params", {})

                if expected_call_kwargs:
                    mock_operator_instance.call.assert_called_with(
                        *expected_call_args, **expected_call_kwargs
                    )
                else:
                    mock_operator_instance.call.assert_called_with(*expected_call_args)
