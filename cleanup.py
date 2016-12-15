import glob
import multiprocessing
import os.path
import pipes

from urllib.parse import urlunparse, urlparse

from lxml import etree, html

parser = html.HTMLParser(encoding='latin-1')
pipeline = pipes.Template()
pipeline.append('pandoc -S -f html -t markdown_github', '--')

def replace_tag(old_element, new_element):
    parent = old_element.getparent()
    parent.insert(parent.index(old_element)+1, new_element)
    parent.remove(old_element)
    new_element.append(old_element)
    old_element.drop_tag()

def remove_empty(node):
    def recursively_empty(e):
        if e.tag == 'br' or e.text and e.text.strip():
            return False
        return all((recursively_empty(c) for c in e.iterchildren()))

    for action, elem in etree.iterwalk(node):
        if recursively_empty(elem):
            elem.drop_tag()

def transform(filename):
    htmlfile = open(filename, encoding='latin-1')
    tree = html.parse(htmlfile, parser=parser)

    # Frontpage seems to use <font> tags to indicate headings
    for node in tree.xpath('//font'):
        size = int(node.get('size')) if 'size' in node.attrib else None
        color = node.get('color').lower() if 'color' in node.attrib else ''
        if color == '#ff0000':
            strong = html.Element('strong')
            replace_tag(node, strong)
        elif size == 6:
            h1 = html.Element('h1')
            replace_tag(node, h1)
        elif size == 5:
            h2 = html.Element('h2')
            replace_tag(node, h2)
        elif size == 4:
            node.drop_tag()

    # We rewrite all the urls to point to MD files instead of HTM
    for node in tree.xpath('//a[@href]'):
        href = node.get('href')

        try:
            parsed_url = urlparse(href)
            path, filename = os.path.split(parsed_url.path)
            basename, extension = filename.split('.')
            hostname = parsed_url.hostname
        except ValueError:
            continue
        else:
            if hostname and hostname.startswith('anastasis'):
                hostname = None

            if extension.startswith('htm'):
                if path:
                    new_path = '{}{}.{}'.format(path.lstrip('/'), basename, 'md')
                else:
                    new_path = '{}.{}'.format(basename, 'md')

                new_url = '', '', new_path, '', '', parsed_url.fragment
                node.set('href', urlunparse(new_url))

    # Pandoc passes this through, cluttering up the final markdown. Must come
    # after footnore rewriting.
    for node in tree.xpath('//span[@class="MsoFootnoteReference"]'):
        node.drop_tag()

    remove_empty(tree)

    return etree.tostring(tree, pretty_print=True, method='html', encoding='unicode')

def convert_html_file(filepath):
    transformed_html = transform(filepath)

    path, filename = os.path.split(filepath)
    basename, extension = filename.split('.')
    output_path = 'files/{}.md'.format(basename)

    f = pipeline.open(output_path, 'w')
    f.write(transformed_html)
    f.close()


if __name__ == '__main__':
    cpu_count = multiprocessing.cpu_count()
    with multiprocessing.Pool(cpu_count) as pool:
        convert_html_file('original/index.html')
        pool.map(convert_html_file, glob.glob('original/*.htm'))
