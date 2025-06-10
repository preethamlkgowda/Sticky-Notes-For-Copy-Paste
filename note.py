import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import json
import os

#intial design
NOTES_DATA_FILE = "sticky_notes_notes_data.json" 
DEFAULT_NOTE_COLOR = "#f9f9b5"
APP_BG_COLOR = "#e0e0e0"
BUTTON_COLOR = "#c0c0c0"
ACCENT_COLOR = "#4682b4"

class NotesApp:
    def __init__(self, root):
        self.root = root
        root.title("Sticky Notes")
        root.geometry("600x550") 
        root.attributes("-topmost", True) 
        root.minsize(400, 400)

        
        self.all_entries_data = []

       
        self.style = ttk.Style()
        self.style.theme_use('clam')

        self.style.configure('TFrame', background=APP_BG_COLOR)
        self.style.configure('TLabel', background=APP_BG_COLOR, font=('Arial', 10))
        self.style.configure('TButton', background=BUTTON_COLOR, font=('Arial', 10))
        self.style.map('TButton', background=[('active', ACCENT_COLOR)])
        self.style.configure('TEntry', font=('Arial', 11))
        self.style.configure('NoteFrame.TFrame', background=DEFAULT_NOTE_COLOR)
        self.style.configure('TitleLabel.TLabel', font=('Arial', 11, 'bold'), background=DEFAULT_NOTE_COLOR)


        
        self.setup_notes_layout(root)

        
        self.load_data()
        root.protocol("WM_DELETE_WINDOW", self.on_closing)
        root.bind("<Control-s>", lambda event=None: self.save_data())
        

    def on_closing(self):
        if messagebox.askokcancel("Quit", "Do you want to save changes before quitting?"):
            self.save_data()
            self.root.destroy()
        else:
            self.root.destroy()

    # Data is saved in a JSON file
    def save_data(self):
        
        data_to_save = {
            "notes": self.all_entries_data
            
        }
        try:
            with open(NOTES_DATA_FILE, "w") as f:
                json.dump(data_to_save, f, indent=4)
            
        except Exception as e:
            print(f"Error saving notes data: {e}")
            messagebox.showerror("Save Error", f"Could not save notes data: {e}")

    def load_data(self):
        
        try:
            if not os.path.exists(NOTES_DATA_FILE):
                raise FileNotFoundError

            with open(NOTES_DATA_FILE, "r") as f:
                loaded_data = json.load(f)
                self.all_entries_data = loaded_data.get("notes", [])
            if hasattr(self, 'entries_frame_container') and self.entries_frame_container.winfo_exists():
                 for widget in self.entries_frame_container.winfo_children():
                     widget.destroy()
            if hasattr(self, 'entries_frame_container'):
                for entry_data in self.all_entries_data:
                    if isinstance(entry_data, dict) and 'text' in entry_data:
                        self.create_collapsible_widget(entry_data)

            
        except FileNotFoundError:
            
            self.all_entries_data = []
            
            if hasattr(self, 'entries_frame_container') and self.entries_frame_container.winfo_exists():
                 for widget in self.entries_frame_container.winfo_children():
                     widget.destroy()

        except json.JSONDecodeError:
            print("Error in the loading the data from the json file")
            
            messagebox.showerror("Load Error", f"{NOTES_DATA_FILE}")
            self.all_entries_data = []
            if hasattr(self, 'entries_frame_container') and self.entries_frame_container.winfo_exists():
                 for widget in self.entries_frame_container.winfo_children():
                     widget.destroy()

        except Exception as e:
            print("Error in loading data from the json")
            messagebox.showerror("Load Error", f"{e}")
            self.all_entries_data = []
            if hasattr(self, 'entries_frame_container') and self.entries_frame_container.winfo_exists():
                 for widget in self.entries_frame_container.winfo_children():
                     widget.destroy()


       
        self.root.after(100, self.update_scroll_regions) 

    def update_scroll_regions(self):
         
         if hasattr(self, 'entries_frame_container') and self.entries_frame_container.winfo_exists():
             self.entries_frame_container.update_idletasks()
             self.canvas_entries.config(scrollregion=self.canvas_entries.bbox("all"))


    
    def setup_notes_layout(self, parent_frame):
        
        input_area_frame = ttk.Frame(parent_frame, style='TFrame')
        input_area_frame.pack(fill="x", padx=10, pady=5)

        title_label = ttk.Label(input_area_frame, text="Title:", style='TLabel')
        title_label.pack(anchor="w", pady=(0, 0))
        self.title_entry = ttk.Entry(input_area_frame, style='TEntry')
        self.title_entry.pack(fill="x", pady=(0, 5))

        input_label = ttk.Label(input_area_frame, text="Paste text here:", style='TLabel')
        input_label.pack(anchor="w", pady=(0, 0))
       
        self.input_text = tk.Text(input_area_frame, height=5, font=("Arial", 11), bg=DEFAULT_NOTE_COLOR, wrap="word", undo=True)
        self.input_text.pack(fill="x", pady=(0, 5))

        button_frame = ttk.Frame(input_area_frame, style='TFrame')
        button_frame.pack(fill="x")
        #Buttons
        submit_btn = ttk.Button(button_frame, text="Add Note", command=self.add_collapsible_entry, style='TButton')
        submit_btn.pack(side="left", pady=5)

        
        save_btn = ttk.Button(button_frame, text="Save Notes", command=self.save_data, style='TButton')
        save_btn.pack(side="left", pady=5, padx=5)


        
        self.canvas_entries = tk.Canvas(parent_frame, bg=APP_BG_COLOR, highlightthickness=0) # Use app bg color
        self.canvas_entries.pack(side="left", fill="both", expand=True, padx=10, pady=5)

        scrollbar_entries = ttk.Scrollbar(parent_frame, orient="vertical", command=self.canvas_entries.yview)
        scrollbar_entries.pack(side="right", fill="y")
        self.canvas_entries.configure(yscrollcommand=scrollbar_entries.set)

        self.entries_frame_container = ttk.Frame(self.canvas_entries, style='TFrame')
        self.canvas_entries.create_window((0, 0), window=self.entries_frame_container, anchor="nw", width=1)


        
        def on_canvas_configure(event):
            canvas_width = event.width
            self.canvas_entries.itemconfig(self.canvas_entries.find_withtag("all")[0], width=canvas_width)
            self.update_scroll_regions()

        self.canvas_entries.bind('<Configure>', on_canvas_configure)


    def add_collapsible_entry(self):
        
        full_text = self.input_text.get("1.0", "end").strip()
        custom_title = self.title_entry.get().strip()

        if not full_text and not custom_title:
             messagebox.showwarning("Input Error", "Please enter some text or a title for the note.")
             return

        
        if not custom_title:
            first_line = full_text.splitlines()[0].strip()
            custom_title = first_line if first_line else "Untitled Note"

        entry_data = {'title': custom_title, 'text': full_text}
        self.all_entries_data.append(entry_data)

        
        self.input_text.delete("1.0", "end")
        self.title_entry.delete(0, "end")

        
        self.create_collapsible_widget(entry_data)

        
        self.update_scroll_regions()

       
        self.save_data()

    def remove_entry(self, entry_data, container):
        
        try:
            self.all_entries_data.remove(entry_data)
            container.destroy()
            print("Note entry removed.")
            self.update_scroll_regions()
            self.save_data() 
        except ValueError:
            print("Error: Note entry data not found in list during removal.")
        except Exception as e:
            print(f"Error removing note entry: {e}")

    def edit_note_text(self, entry_data, text_widget, container):
        
        edit_window = tk.Toplevel(self.root)
        edit_window.title("Edit Note")
        edit_window.geometry("500x400")
        edit_window.transient(self.root) 
        edit_window.grab_set() 
        edit_window.focus_set() 

        
        edit_text_widget = tk.Text(edit_window, font=("Arial", 11), wrap="word", bg="white", undo=True)
        edit_text_widget.pack(fill="both", expand=True, padx=10, pady=10)
        edit_text_widget.insert("1.0", entry_data['text'])

        def save_edit():
            new_text = edit_text_widget.get("1.0", "end").strip()
            
            if new_text != entry_data['text']:
                entry_data['text'] = new_text
                
                if text_widget and text_widget.winfo_exists(): 
                     text_widget.config(state="normal")
                     text_widget.delete("1.0", "end")
                     text_widget.insert("1.0", new_text)
                     text_widget.config(state="disabled")

                
                title_label_widget = None
                for child in container.winfo_children():
                    if isinstance(child, tk.Frame): 
                        for grand_child in child.winfo_children():
                           
                            if isinstance(grand_child, ttk.Label) and grand_child.cget('text') not in ["Edit Text", "Copy", "Delete"]:
                                title_label_widget = grand_child
                                break
                    if title_label_widget: break

                if title_label_widget:
                    
                     old_text_snippet = entry_data.get('text', '').splitlines()[0].strip() if entry_data.get('text', '') else "Empty Note"
                     if len(old_text_snippet) > 60: old_text_snippet = old_text_snippet[:57] + "..."

        
                     
                     if title_label_widget.cget('text') == old_text_snippet or not entry_data.get('title', ''):
                         new_title = new_text.splitlines()[0].strip() if new_text else "Untitled Note"
                         entry_data['title'] = new_title 
                         snippet_to_display = new_title
                         if len(snippet_to_display) > 60: snippet_to_display = snippet_to_display[:57] + "..."
                         title_label_widget.config(text=snippet_to_display) 

                self.save_data() 
                print("Note text updated.")
            edit_window.destroy()

        def cancel_edit():
            edit_window.destroy()

        button_frame = ttk.Frame(edit_window, style='TFrame')
        button_frame.pack(fill="x", pady=(0, 10))

        save_button = ttk.Button(button_frame, text="Save", command=save_edit, style='TButton')
        save_button.pack(side="right", padx=5)

        cancel_button = ttk.Button(button_frame, text="Cancel", command=cancel_edit, style='TButton')
        cancel_button.pack(side="right")

        
        self.root.wait_window(edit_window)

    def edit_note_title(self, event, label_widget, container, entry_data):
       
        parent = label_widget.master

        
        label_info = label_widget.pack_info() 
        label_widget.pack_forget() 

        
        edit_entry = ttk.Entry(parent, font=label_widget.cget('font'), style='TEntry')
       
        edit_entry.pack(**label_info)


        edit_entry.insert(0, entry_data.get('title', '')) 
        edit_entry.focus_set()


        
        original_double_click_bind_cmd = label_widget.bind("<Double-Button-1>")
        label_widget.unbind("<Double-Button-1>")


        def save_title(event=None):
            new_title = edit_entry.get().strip()
            
            if not new_title:
                new_title = entry_data.get('text', '').splitlines()[0].strip() if entry_data.get('text', '').strip() else "Untitled Note"
                messagebox.showinfo("Note Title", "Title cannot be empty. Setting default from note content.")

            
            if new_title != entry_data.get('title', ''):
                entry_data['title'] = new_title
                snippet = new_title
                if len(snippet) > 60: snippet = snippet[:57] + "..."
                label_widget.config(text=snippet)
                self.save_data() 
                print("Note title updated.")

            edit_entry.destroy() 
            label_widget.pack(**label_info) 
            label_widget.bind("<Double-Button-1>", original_double_click_bind_cmd)


        def cancel_title(event=None):
             edit_entry.destroy() 
             label_widget.pack(**label_info) 
             
             label_widget.bind("<Double-Button-1>", original_double_click_bind_cmd)


        edit_entry.bind("<Return>", save_title)      
        edit_entry.bind("<FocusOut>", save_title)   


    def toggle_note_text(self, text_widget):
        
        if not text_widget or not text_widget.winfo_exists(): return 

        if text_widget.winfo_ismapped():
            text_widget.pack_forget()
        else:
            
            text_widget.config(state="normal")
            
            content = text_widget.get("1.0", "end-1c")
            num_lines = content.count('\n') + (1 if content else 0) 

            
            approx_height = max(3, min(15, num_lines + 1)) 
            text_widget.config(height=approx_height, state="disabled")
            text_widget.pack(fill="both", expand=True, padx=10, pady=5)

        
        self.root.after(10, self.update_scroll_regions)


    def create_collapsible_widget(self, entry_data):
        
        container = ttk.Frame(self.entries_frame_container, style='NoteFrame.TFrame')
        container.pack(fill="x", pady=3, padx=5) 

        
        top_row = ttk.Frame(container, style='NoteFrame.TFrame')
        top_row.pack(fill="x", expand=True)

        
        full_text = entry_data.get('text', '')
        title = entry_data.get('title', '')
        snippet_text = title if title else full_text.splitlines()[0].strip() if full_text.strip() else "Empty Note"
        if len(snippet_text) > 60:
            snippet_text = snippet_text[:57] + "..."

        
        label = ttk.Label(top_row, text=snippet_text, anchor="w", style='TitleLabel.TLabel')
        
        
        delete_btn = ttk.Button(top_row, text="Delete", command=lambda data=entry_data, cont=container: self.remove_entry(data, cont), style='TButton')
        delete_btn.pack(side="right", padx=(0, 10), pady=5)

        
        copy_btn = ttk.Button(top_row, text="Copy", command=lambda text=full_text: self.root.clipboard_clear() or self.root.clipboard_append(text), style='TButton')
        copy_btn.pack(side="right", padx=(0, 5), pady=5)

        
        full_text_widget = tk.Text(container, font=("Arial", 11), bg=DEFAULT_NOTE_COLOR, height=1, wrap="word", bd=0, highlightthickness=0) # Added highlightthickness=0
        full_text_widget.insert("1.0", full_text)
        full_text_widget.config(state="disabled", relief="flat") 

        
        edit_btn = ttk.Button(top_row, text="Edit Text", command=lambda data=entry_data, txt_w=full_text_widget, cont=container: self.edit_note_text(data, txt_w, cont), style='TButton')
        edit_btn.pack(side="right", padx=(0, 5), pady=5)

        
        label.pack(side="left", fill="x", expand=True, padx=10, pady=5)


        
        label.bind("<Double-Button-1>", lambda event: self.toggle_note_text(full_text_widget))

        
        label.bind("<Button-1>", lambda event: self.edit_note_title(event, label, container, entry_data))



if __name__ == "__main__":
    root = tk.Tk()
    app = NotesApp(root)
    root.mainloop()