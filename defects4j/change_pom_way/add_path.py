import os
import json
import xml.etree.ElementTree as ET

# Path to the JSON file listing projects and bug numbers
JSON_LIST_FILE = 'sft_qwen3_llama_result.json'
# Base directory containing all buggy project folders
BASE_DIR = 'projects_b_test_2'
# Reference ID to add
REFID = 'd4j.lib.testgen.rt'


def ensure_classpath(javac_elem):
    """
    Ensure that the <javac> element contains a <classpath> with the specified <path refid>.
    """
    # Check existing classpath entries
    for cp in javac_elem.findall('classpath'):
        # Case 1: <classpath refid="..."/>
        if cp.get('refid') == REFID:
            return False
        # Case 2: <classpath><path refid="..."/></classpath>
        for path in cp.findall('path'):
            if path.get('refid') == REFID:
                return False
    # Not found: add new classpath element
    cp = ET.SubElement(javac_elem, 'classpath')
    path = ET.SubElement(cp, 'path')
    path.set('refid', REFID)
    return True


def process_build_file(filepath):
    """
    Process a build.xml or maven-build.xml file, adding classpath to <javac> in <target name=compile-tests|compile.tests>.
    Returns True if modified.
    """
    tree = ET.parse(filepath)
    root = tree.getroot()
    modified = False

    # Find targets of interest
    for target in root.findall('target'):
        name = target.get('name', '')
        if name in ('compile-tests', 'compile.tests'):
            # Look for javac elements under this target
            javacs = target.findall('.//javac')
            if javacs:
                for javac in javacs:
                    if ensure_classpath(javac):
                        modified = True
            else:
                # No javac here; skip and let caller decide to try maven-build.xml
                return False
    if modified:
        # Write back with simple formatting
        ET.indent(tree, space="    ")  # Python 3.9+
        tree.write(filepath, encoding='utf-8', xml_declaration=True)
    return modified


def main():
    # Load list of projects
    with open(JSON_LIST_FILE, 'r', encoding='utf-8') as f:
        projects = json.load(f)

    for entry in projects:
        project = entry['project']
        bug_num = entry['bug_num']
        # Construct folder name (e.g., lang_5_fixed)
        folder_name = f"{project.lower()}_{bug_num}_buggy"
        project_path = os.path.join(BASE_DIR, folder_name)

        # Special case for Gson
        if project.lower() == 'gson':
            project_path = os.path.join(project_path, 'gson')

        if not os.path.isdir(project_path):
            print(f"Warning: {project_path} does not exist, skipping.")
            continue

        # Look for build.xml first
        build_xml = os.path.join(project_path, 'build.xml')
        maven_xml = os.path.join(project_path, 'maven-build.xml')
        done = False

        if os.path.isfile(build_xml):
            print(f"Processing {build_xml}")
            if process_build_file(build_xml):
                print(f"Modified {build_xml}")
                done = True
            else:
                print(f"No <javac> in compile-tests of {build_xml}, will try maven-build.xml.")

        if not done and os.path.isfile(maven_xml):
            print(f"Processing {maven_xml}")
            if process_build_file(maven_xml):
                print(f"Modified {maven_xml}")
            else:
                print(f"No <javac> in compile-tests of {maven_xml}, no changes made.")

if __name__ == '__main__':
    main()
