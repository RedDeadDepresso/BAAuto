from bs4 import BeautifulSoup
import requests
import json
import concurrent.futures

def generate_urls():
    urls = []
    html_file = requests.get('https://ba.gamekee.com/').text
    soup = BeautifulSoup(html_file, 'lxml')
    div = soup.find_all('div',class_ = "item-wrapper icon-size-6 pc-item-group")
    a = div[1].find_all('a')
    for link in a: 
        urls.append(link.get('href'))
    return urls

def find_student_name(url):
    r = requests.get('https://ba.gamekee.com' + url).text
    soup = BeautifulSoup(r, 'lxml')
    tables = soup.find_all('table', class_='mould-table selectItemTable col-group-table')
    for table in tables:
        for span in table.find_all('span'):
            if span.text == "学生信息":
                target_row = table.find_all('tr')[2] 
                target_cell = target_row.find_all('td')[1]  

                # Get the text inside the cell
                text = target_cell.get_text()

                # Print the text
                print('https://ba.gamekee.com' + url)
                print(text.strip())
                return text.strip()
            

def main():
    urls = generate_urls()
    student_names = set()  # Create an empty list to store the results
    with concurrent.futures.ThreadPoolExecutor() as executor:
        # Use submit to schedule tasks and collect Future objects
        futures = [executor.submit(find_student_name, url) for url in urls]

        # Use as_completed to iterate over completed futures
        for future in concurrent.futures.as_completed(futures):
            result = future.result()  # Get the result from the completed future
            if result is None or any(char.isdigit() for char in result):
                print("Anomaly\n")

            elif result in student_names:
                student_names.remove(result)
                print("Anomaly\n")
            else:
                print("\n")
                student_names.add(result)  # Append the result to the list

    # Now student_names contains all the collected student names
    student_names = list(student_names)
    student_names.sort()
    with open("CN_student_list.json", "w") as f:
        json.dump(student_names, f, indent=2)

if __name__ == '__main__':
    main()
