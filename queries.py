import pandas as pd
import tkinter.simpledialog as simple_dialog
import tkinter.messagebox as messagebox


def query_person_info(familytree):

    if familytree is not None:
        query = simple_dialog.askstring("Query Family Member", "Enter Name or ID:")

        if query:
            results = familytree[(familytree['ID'] == query) | (familytree['Person'] == query)]

            if not results.empty:
                details = []

                for _, row in results.iterrows():
                    person_details = f"Name: {row['Person']}\nID: {row['ID']}\n"
                    fields = ['Generation', 'Gender', 'Birth', 'Death', 'Marriage', 'Children', 'Address', 'Occupation',
                              'Buried', 'Notes']

                    for field in fields:

                        if not pd.isna(row[field]) and row[field]:

                            if field == 'Generation':
                                field_value = int(row[field]) if pd.api.types.is_number(row[field]) else row[field]
                            else:
                                field_value = str(row[field]).replace('\\n', '\n\t')

                            person_details += f"{field}: {field_value}\n"

                    details.append(person_details.strip())

                messagebox.showinfo("Query Result", "\n\n".join(details))

            else:
                messagebox.showwarning("Not Found", "No matching person found for your query.")

        else:
            messagebox.showerror("Error", "No family tree loaded.")
