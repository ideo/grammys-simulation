import yaml


def load_text():
    filepath = "src/text.yml"
    text = open_yml_file(filepath)
    return text


def open_yml_file(filepath):
    with open(filepath, "r") as stream:
        try:
            messages = yaml.safe_load(stream)
            return messages
        except yaml.YAMLError as exc:
            print(exc)
    

if __name__ == "__main__":
    filepath = "src/text.yml"
    story = open_yml_file(filepath)
    print(story)