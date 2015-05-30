#!/usr/bin/env python3
"""
This script will generate a package with a single plugin based on the parameters
passed in.
"""
import argparse
import os, sys

# File templates
plugin_py = \
"""import plugintypes

class {plugin_name}Plugin(plugintypes.TelegramPlugin):
    patterns = {{
        "^!command": "callback",
    }}

    usage = [
        "!command: Help here",
    ]

    def callback(self, msg, matches):
        return "Response Here"
"""

plugin_plugin = \
"""[Core]
Name = {plugin_name}
Module = {module_name}

[Documentation]
{author}{version}{website}{description}
"""

repos_json = \
"""{{
    "name": "{package_name}",
    "description": "{description}",
    {version}
    "default_enable": ["{package_name}"],
    {website}
    "repo": "{repo}"
}}
"""

readme_md = \
"""
# {output}
{description}
"""


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Generate telegram-pybot package.')
    parser.add_argument('-p', '--package', dest="package_name", required=True,
                        help="Package name, will also be used for the plugin name.")
    parser.add_argument('-o', '--output', dest="output", required=True,
                        help="Directory to create for package. Must just be a directory name, no path.")
    parser.add_argument('-r', '--repo', dest="repo",
                        help="Git repo where plugin is hosted.")
    parser.add_argument('-d', '--desc', dest="desc",
                        help="Description of the package/plugin.")
    parser.add_argument('-a', '--author', dest="author",
                        help="Author of the package.")
    parser.add_argument('-w', '--website', dest="website",
                        help="Website for package, most likely a git URL.")
    parser.add_argument('-v', '--version', dest="version",
                        help="Version of the package. If not set, will use git rev.")

    opts = parser.parse_args()

    out_plugin_py = plugin_py.format(plugin_name=opts.package_name)
    out_plugin_plugin = plugin_plugin.format(plugin_name=opts.package_name,
                                             module_name=opts.package_name.lower(),
                                             author="Author = {}\n".format(opts.author) if opts.author else '',
                                             version="Version = {}\n".format(opts.version) if opts.version else '',
                                             website="Website = {}\n".format(opts.website) if opts.website else '',
                                             description="Description = {}\n".format(opts.desc) if opts.desc else ''
                                      )
    out_repos_json = repos_json.format(package_name=opts.package_name,
                                       description=opts.desc if opts.desc else '',
                                       version='"version": "{}",'.format(opts.version) if opts.version else '"version": "1.0",',
                                       website='"homepage": "{}",'.format(opts.website) if opts.website else '"homepage": "{}"'.format(opts.repo),
                                       # The default is very datamachine centric, others probably want to specify their own
                                       repo=opts.repo if opts.repo else "http://github.com/datamachine/telegram-pybot-{}".format(opts.output)
                                )
    out_readme_md = readme_md.format(output=opts.output, \
                                     description=opts.desc if opts.desc else ''
                              )

    if not os.path.exists(opts.output):
        os.makedirs(opts.output)
        os.makedirs("{}/repository".format(opts.output))
    else:
        print("Output exists! Exiting...")
        sys.exit(0)

    with open("{}/{}.py".format(opts.output, opts.package_name.lower()), 'w') as f:
        f.write(out_plugin_py)
    with open("{}/{}.plugin".format(opts.output, opts.package_name.lower()), 'w') as f:
        f.write(out_plugin_plugin)
    with open("{}/README.md".format(opts.output), 'w') as f:
        f.write(out_readme_md)
    with open("{}/repository/repos.json".format(opts.output), 'w') as f:
        f.write(out_repos_json)
    with open("{}/repository/requirements.txt".format(opts.output), 'w') as f:
        f.write("")

