import customtkinter
import CTkListbox

class MyCTkListbox(CTkListbox.CTkListbox):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.grid_columnconfigure(0, weight=0)

    def insert(self, index, option, **args):
        """add new option in the listbox"""

        if str(index).lower() == "end":
            index = f"END{self.end_num}"
            self.end_num += 1

        if index in self.buttons:
            self.buttons[index].grid_remove()
            self.buttons[index].destroy()

        self.buttons[index] = customtkinter.CTkButton(
            self,
            text=option,
            fg_color=self.button_fg_color,
            anchor=self.justify,
            text_color=self.text_color,
            font=self.font,
            hover_color=self.hover_color,
            **args,
        )
        self.buttons[index].configure(command=lambda num=index: self.select(num))
        self.buttons[index].grid(row=index, column=0, padx=5, pady=(0, 5), sticky="w")
        self.update()

        if self.multiple:
            self.buttons[index].bind(
                "<Shift-1>", lambda e: self.select_multiple(self.buttons[index])
            )

        return self.buttons[index]

    def delete(self, index, last=None):
        """delete options from the listbox"""
        if str(index).lower() == "all":
            for i in self.buttons:
                self.buttons[i].grid_remove()
                self.buttons[i].destroy()
            self.buttons = {}
            self.end_num = 0
            return

        if str(index).lower() == "end":
            index = f"END{self.end_num}"
            self.end_num -= 1
        else:
            if int(index) >= len(self.buttons):
                return
            if not last:
                index = list(self.buttons.keys())[int(index)]

        if last:
            if str(last).lower() == "end":
                last = len(self.buttons) - 1
            elif int(last) >= len(self.buttons):
                last = len(self.buttons) - 1

            deleted_list = []
            for i in range(int(index), int(last) + 1):
                list(self.buttons.values())[i].grid_remove()
                list(self.buttons.values())[i].destroy()
                deleted_list.append(list(self.buttons.keys())[i])
                self.update()
            for i in deleted_list:
                del self.buttons[i]
        else:
            self.buttons[index].grid_remove()
            self.buttons[index].destroy()
            if self.multiple:
                if self.buttons[index] in self.selections:
                    self.selections.remove(self.buttons[index])
            del self.buttons[index]