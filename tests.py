import unittest
import posixpath
from docutils import nodes
from typing import Any, List, Tuple


# NOTE: The code below contains minimal class definitions (MockApp, MockDoctree, etc.)
# to simulate the necessary Sphinx objects. This avoids "mocking" the tested function's
# logic, instead fabricating the environment required for execution.

# --- Minimal Classes for Test Environment ---

class MockDoctree(list):
    """A list that records appends and acts like a docutils doctree."""

    def append(self, item):
        """Overrides list append to record the last appended item."""
        self.append_called_with = item
        super().append(item)


class MockBuilder:
    """A minimal class to simulate the Sphinx builder (contains the format attribute)."""

    def __init__(self, format: str = 'html'):
        self.format = format


class MockApp:
    """A minimal class to simulate the Sphinx application (contains connect/add_css_file)."""

    def __init__(self, builder_format: str = 'html'):
        self.connect_calls: List[Tuple[str, Any]] = []
        self.add_css_calls: List[str] = []
        self.builder = MockBuilder(builder_format)
        # Required attributes for setup() if a full build were run
        self.config = unittest.mock.MagicMock()

    def connect(self, event: str, function: Any):
        """Records the event and handler function."""
        self.connect_calls.append((event, function))

    def add_css_file(self, filename: str):
        """Records the added CSS file."""
        self.add_css_calls.append(filename)


# --- Code Under Test (Redefinition for standalone test file) ---

def add_llm_link_node(app: MockApp, doctree: MockDoctree, docname: str):
    """
    The handler function logic: injects a nodes.raw element containing the link
    to the sibling .txt file.
    """
    if app.builder.format != 'html':
        return

    # Use posixpath.basename to correctly handle docnames (e.g., 'guide/install')
    current_filename = posixpath.basename(docname)
    relative_link = f"{current_filename}.txt"

    html_content = f'''
    <div class="sphinx-llms-txt-link-container">
        <a href="{relative_link}" class="sphinx-llms-txt-link">
            View llms.txt version
        </a>
    </div>
    '''

    raw_node = nodes.raw('', html_content, format='html')
    doctree.append(raw_node)


def setup(app: MockApp):
    """
    The setup function: registers the handler and CSS file.
    """
    app.connect('doctree-resolved', add_llm_link_node)
    app.add_css_file('llm_link.css')

    return {
        'version': '0.3',
        'parallel_read_safe': True,
        'parallel_write_safe': True
    }


# --- Test Cases ---

class TestSphinxLlmLink(unittest.TestCase):

    def test_01_setup_registers_hooks_and_css(self):
        """Verifies that setup() correctly registers the doctree hook and the CSS file."""
        app = MockApp()
        ret = setup(app)

        # 1. Check connect hook for 'doctree-resolved'
        self.assertIn(('doctree-resolved', add_llm_link_node),
                      app.connect_calls)

        # 2. Check CSS file inclusion
        self.assertIn('sphinx_llms_txt_link.css', app.add_css_calls)

        # 3. Check return dictionary metadata
        self.assertEqual(ret['version'], '0.3')

    def assert_raw_node_and_link(self, doctree: MockDoctree,
                                 expected_link: str):
        """Helper to assert the last node is raw HTML and contains the correct link."""
        self.assertGreater(len(doctree), 0,
                           "No node was appended to the doctree.")
        injected_node = doctree[-1]
        self.assertIsInstance(injected_node, nodes.raw,
                              "The appended node is not a docutils.nodes.raw.")
        self.assertEqual(injected_node['format'], 'html',
                         "Raw node format must be 'html'.")
        self.assertIn(f'href="{expected_link}"', injected_node.astext(),
                      "Injected link does not match expected relative path.")
        self.assertIn('sphinx-llms-txt-link-container', injected_node.astext(),
                      "HTML content is missing the expected CSS class.")

    def test_02_node_injection_for_root_document(self):
        """Tests link generation for a root document (e.g., index.rst)."""
        app = MockApp(builder_format='html')
        doctree = MockDoctree()
        docname = 'index'

        add_llm_link_node(app, doctree, docname)

        self.assert_raw_node_and_link(doctree, 'index.txt')

    def test_03_node_injection_for_nested_document(self):
        """Tests link generation for a document in a subfolder (e.g., guide/install.rst)."""
        app = MockApp(builder_format='html')
        doctree = MockDoctree()
        # This docname requires posixpath.basename to extract 'install'
        docname = 'guide/install'

        add_llm_link_node(app, doctree, docname)

        # The correct relative link should only be the filename, not the path
        self.assert_raw_node_and_link(doctree, 'install.txt')

    def test_04_node_injection_for_deeply_nested_document(self):
        """Tests link generation for a deeply nested document (e.g., api/v2/auth/token.rst)."""
        app = MockApp(builder_format='html')
        doctree = MockDoctree()
        docname = 'api/v2/auth/token'

        add_llm_link_node(app, doctree, docname)

        # The correct relative link should be 'token.txt'
        self.assert_raw_node_and_link(doctree, 'token.txt')

    def test_05_non_html_builder_is_skipped(self):
        """Tests that the function returns early for non-HTML builders (e.g., latex)."""
        app = MockApp(builder_format='latex')
        doctree = MockDoctree()
        docname = 'index'

        add_llm_link_node(app, doctree, docname)

        # The doctree must remain empty
        self.assertEqual(len(doctree), 0,
                         "Doctree was modified for a non-HTML builder.")


if __name__ == '__main__':
    # To run these tests, save this code as a Python file and execute it.
    # Note: Requires docutils to be installed (which Sphinx requires).
    unittest.main()
