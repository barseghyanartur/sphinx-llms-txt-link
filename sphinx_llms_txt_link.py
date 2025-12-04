import os
from docutils import nodes
from sphinx.util.fileutil import copy_asset


__title__ = "sphinx-llms-txt-link"
__version__ = "0.1"
__author__ = "Artur Barseghyan <artur.barseghyan@gmail.com>"
__copyright__ = "2025 Artur Barseghyan"
__license__ = "MIT"
__all__ = (
    "add_llm_link_node",
    "copy_custom_css",
    "setup",
    "add_static_path",
)


def add_llm_link_node(app, doctree, docname):
    if app.builder.format != 'html':
        return

    llm_page_name = f"{docname}.txt"
    relative_link = app.builder.get_relative_uri(docname, llm_page_name)

    # Cleaner HTML without inline styles
    html_content = f'''
    <div class="llm-link-container">
        <a href="{relative_link}" class="llm-link">
            View llms.txt version
        </a>
    </div>
    '''

    raw_node = nodes.raw('', html_content, format='html')
    doctree.append(raw_node)


def copy_custom_css(app, exception):
    # This hook ensures the CSS file is copied to the build static directory
    if app.builder.format == 'html' and not exception:
        # Assuming the css file is in a folder named '_static' relative to this script
        # You might need to adjust based on your package structure
        # For this example, we'll assume you ship a file named 'llm_link.css'
        pass
        # In a real plugin, you'd use sphinx.util.fileutil.copy_asset here
        # to move your packaged CSS to the output _static folder.


def setup(app):
    app.connect('doctree-resolved', add_llm_link_node)

    # Inject the CSS file reference into the HTML <head>
    # You will need to ship this file with your extension
    app.add_css_file('sphinx_llms_txt_link.css')

    # Standard way for plugins:
    # Use app.connect('builder-inited', ...) to append to html_static_path
    app.connect('builder-inited', add_static_path)

    return {
        'version': '0.2',
        'parallel_read_safe': True,
        'parallel_write_safe': True
    }


def add_static_path(app):
    # This assumes 'assets' is a folder inside your python package
    # containing llm_link.css
    static_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'assets'))
    app.config.html_static_path.append(static_path)