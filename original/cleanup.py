import glob
import pipes

from lxml import etree, html

from multiprocessing import Pool


def replace_tag(old_element, new_element):
    parent = old_element.getparent()
    parent.insert(parent.index(old_element)+1, new_element)
    parent.remove(old_element)
    new_element.append(old_element)
    old_element.drop_tag()

def transform(filename):
    htmlfile = open(filename, encoding='ISO-8859-1')
    tree = html.parse(htmlfile)

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

    for node in tree.xpath('//a[@href]'):
        href = node.get('href')

        try:
            basename, extension = href.split('.')
        except ValueError:
            continue

        if extension.startswith('htm'):
            node.set('href', '{}.{}'.format(basename, 'md'))

    #for node in tree.xpath('//p[re:test(@align, "^center$", "i")]', namespaces={"re": "http://exslt.org/regular-expressions"}):
    #    node.set('align', None)

    transformed_html = etree.tostring(tree, pretty_print=True, method='html', encoding='unicode')
    return transformed_html


def convert_html_file(filename):
    basename, extension = filename.split('.')
    pandoc = 'pandoc -S -f html -t markdown_github'

    transformed_html = transform(filename)

    t = pipes.Template()
    t.append(pandoc, '--')
    f = t.open('{}.md'.format(basename), 'w')
    f.write(transformed_html)
    f.close()


if __name__ == '__main__':
    with Pool(8) as pool:
        convert_html_file('index.html')
        pool.map(convert_html_file, glob.glob('*.htm'))
        #for filename in glob.glob('*.htm'):
        #    convert_html_file(filename)
