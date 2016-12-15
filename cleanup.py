import glob
import multiprocessing
import os.path
import pipes

from lxml import etree, html

parser = html.HTMLParser(encoding='latin-1')
pipeline = pipes.Template()
pipeline.append('pandoc -S -f html -t commonmark', '--')

def replace_tag(old_element, new_element):
    parent = old_element.getparent()
    parent.insert(parent.index(old_element)+1, new_element)
    parent.remove(old_element)
    new_element.append(old_element)
    old_element.drop_tag()

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
            basename, extension = href.split('.')
        except ValueError:
            continue
        else:
            if extension.startswith('htm'):
                node.set('href', '{}.{}'.format(basename, 'md'))

    # Pandoc passes this through, cluttering up the final markdown
    for node in tree.xpath('//span[@class="MsoFootnoteReference"]'):
        node.drop_tag()

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
