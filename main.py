import flet as ft
from config import *
from db import AppDB
from aiosqlite.core import sqlite3

AppDB = AppDB('sqlite+aiosqlite:///database.db')

async def main(page: ft.Page):
    page.title = TITLE
    page.window_width= WIDTH

    item_count_list = []
    
    await AppDB.connect()

    async def next_step(e):
        result = await AppDB.get_item_data(bcode_field.value)
        try:
            result = list(result[0])
            name_field.value, quantity_field.value, cost_field.value = result[2], result[3], result[4]
            name_field.disabled, quantity_field.disabled, cost_field.disabled = False, False, False
            next_button.visible, save_button.visible = False, True
            await page.update_async()
        except IndexError:
            name_field.disabled, quantity_field.disabled, cost_field.disabled = False, False, False
            await name_field.focus_async()
            next_button.visible, save_button.visible = False, True
            await page.update_async()

    async def data_save(e):
        if bcode_field.value =='' or name_field.value == '' or quantity_field.value == '' or cost_field.value == '':
            if bcode_field.value == '':
                bcode_field.border_color = "#ff0000"
            else:
                bcode_field.border_color = "#09E109"
            if name_field.value == '':
                name_field.border_color = "#ff0000"
            else:
                name_field.border_color = "#09E109"
            if quantity_field.value == '':
                quantity_field.border_color = "#ff0000"
            else:
                quantity_field.border_color = "#09E109"
            if cost_field.value == '':
                cost_field.border_color = "#ff0000"
            else:
                cost_field.border_color = "#09E109"
            finish_text.value = "Hamma ma`lumotlarni kiriting!"
            finish_text.color = "#ff0000"
            finish_text.visible = True
            await page.update_async()
        else:
            try:
                await AppDB.save_new_data(bcode_field.value, name_field.value, quantity_field.value, cost_field.value)

            except sqlite3.IntegrityError:
                await AppDB.renew_data(bcode_field.value, name_field.value, quantity_field.value, cost_field.value)

            bcode_field.value, name_field.value, quantity_field.value, cost_field.value = '','','',''
            finish_text.value = 'Saqlandi'
            finish_text.color = "#09E109"
            finish_text.visible = True
            bcode_field.border_color, name_field.border_color, quantity_field.border_color, cost_field.border_color = "#09E109","#09E109","#09E109","#09E109"
            name_field.disabled, quantity_field.disabled, cost_field.disabled = True, True, True
            save_button.visible, next_button.visible = False, True
            await page.update_async()
    
    async def data_read(e):
        result = await AppDB.get_item_data(bcode_field.value)
        bcode_field.value = ""
        try:
            result = list(result[0])
            bc_out.value = result[1]
            name_out.value = result[2]
            qtty_out.value = result[3]
            cost_out.value = result[4]
            await page.update_async()
            print(result)
        except IndexError:
            bc_out.value = "Bunday tovar mavjud emas."
            name_out.value, qtty_out.value, cost_out.value = "", "", ""
            await page.update_async()
    
    checkout_items = {}
    
    async def add_item(e):
        result = await AppDB.get_item_data(bcode_field.value)
        bcode_field.value = ''
        try:
            result = list(result[0])
            result[0] = len(chck_list.controls) + 1
            item_count = 1
            item_count_list.append(item_count)
            item_info = ft.Row()
            item_info.controls.append(ft.Container(
                width=100,
                        padding = 10,
                        margin = 0,
                        border_radius=ft.border_radius.all(10),
                        border=ft.border.all(1, "#09E109"),
                        content=ft.Text(value=result[0], weight='bold', size=16, text_align='right')
            ))
            item_info.controls.append(ft.Container(
                width=350,
                        padding = 10,
                        margin = 0,
                        border_radius=ft.border_radius.all(10),
                        border=ft.border.all(1, "#09E109"),
                        content=ft.Text(value=result[2], weight='bold', size=16, text_align='right')   
            ))
            item_info.controls.append(ft.Container(
                width=100,
                padding = 10,
                        margin = 0,
                        border_radius=ft.border_radius.all(10),
                        border=ft.border.all(1, "#09E109"),
                        content=ft.Text(value=item_count, weight='bold', size=16, text_align='right')
            ))
            item_info.controls.append(ft.Container(
                width=250,
                padding = 10,
                        margin = 0,
                        border_radius=ft.border_radius.all(10),
                        border=ft.border.all(1, "#09E109"),
                        content=ft.Text(value=result[4], weight='bold', size=16, text_align='right')
            ))
            chck_list.controls.append(item_info)
            total_price.value += result[4]
            conf_text.visible = False
            if result[1] in checkout_items:
                checkout_items[result[1]] += item_count
            else:
                checkout_items[result[1]] = item_count

        except IndexError:
            conf_text.visible = True
        await bcode_field.focus_async()
        await page.update_async()
    
    async def checkout(e):
        for x in checkout_items:
            quantity = await AppDB.get_item_quantity(x)
            quantity = quantity - checkout_items[x]
            await AppDB.renew_quantity(x, quantity)
            await chck_list.clean_async()
            total_price.value = 0
            await page.update_async()
        checkout_items.clear()
        print(checkout_items)

    async def extra_dialog_open(e):
        page.dialog = extra_items_dialog
        extra_items_dialog.open = True
        await page.update_async()
    
    async def add_extra_item(e):
        page.dialog = count_dialog
        count_dialog.open = True
        await page.update_async()        

    bcode_field = ft.TextField(text_align="right", width=400, autofocus=True, keyboard_type=ft.KeyboardType.NUMBER, border_color="#09E109", on_submit=next_step)
    name_field = ft.TextField(text_align="right", width=400, border_color="#09E109", disabled=True)
    quantity_field = ft.TextField(text_align="right", width=400, border_color="#09E109", disabled=True)
    cost_field = ft.TextField(text_align="right", width=400, border_color="#09E109", disabled=True)
    finish_text = ft.Text(weight='bold', text_align='center', color="#09E109", value="Saqlandi", visible=False)
    next_button = ft.ElevatedButton(visible=True, text = "Keyingi", on_click=next_step)
    save_button = ft.ElevatedButton(visible=False, text= "Saqlash", on_click=data_save ,autofocus=True)

    srch_bttn = ft.ElevatedButton(text="Qidirish", on_click=data_read)
    bc_out = ft.Text(text_align="left", width=150, weight="bold")
    name_out = ft.Text(text_align="left", width=150, weight="bold")
    qtty_out = ft.Text(text_align="left", width=100, weight="bold")
    cost_out = ft.Text(text_align="left", width=100, weight="bold")

    chck_list = ft.Column(height=250, scroll=ft.ScrollMode.AUTO, auto_scroll=True)
    conf_text = ft.Text(weight='bold', color="#ff0000", visible=False, value='Bunday tovar mavjud emas!')
    total_price = ft.Text(weight='bold', size=24, text_align='right', value=0)

    count_dialog = ft.AlertDialog(title=ft.Text(value="Soni"), content=ft.Column(controls=[
        ft.Row(controls=[
            ft.Text(value="Qo`shish sonini kiriting"),
        ]),
        ft.Row(controls=[
            ft.TextField(width=300)
        ]),
        ft.Row(controls=[
            ft.ElevatedButton(text="Qo`shish"),
            ft.ElevatedButton(text="Yopish")
        ])
    ]))

    income_container = ft.Container(
        width=1000,
        padding=20,
        border_radius=ft.border_radius.all(20),
        content=ft.Column(controls=[
            ft.Row(controls=[
                ft.Text(weight="bold", text_align="right", value="Bar-code:", size=24)
            ]),
            ft.Row(controls=[
                bcode_field
            ]),
            ft.Row(controls=[
                ft.Text(weight="bold", text_align="right", value="Tovar nomi:", size=24)
            ]),
            ft.Row(controls=[
                name_field
            ]),
            ft.Row(controls=[
                ft.Text(weight="bold", text_align="right", value="Soni:", size=24)
            ]),
            ft.Row(controls=[
                quantity_field
            ]),
            ft.Row(controls=[
                ft.Text(weight="bold", text_align="right", value="Donasining narxi:", size=24)
            ]),
            ft.Row(controls=[
                cost_field
            ]),
            ft.Row(controls=[
                next_button,
                save_button
            ]),
            ft.Row(controls=[
                finish_text
            ])
        ])
    )

    search_container = ft.Container(
        width=800,
        padding=20,
        border_radius=ft.border_radius.all(20),
        content=ft.Column(controls=[
            ft.Row(controls=[
                ft.Text(weight="bold", text_align="right", value="Bar-code:", size=24)
            ]),
            ft.Row(controls=[
                bcode_field
            ]),
            ft.Row(controls=[
                srch_bttn
            ])
        ])
    )

    output_container = ft.Container(
        width=600,
        padding=20,
        border_radius=ft.border_radius.all(20),
        border=ft.border.all(1, "#09E109"),
        content=ft.Column(controls=[
            ft.Row(controls=[
                ft.Text(value="Bar code", text_align="left", width=150, weight="bold", no_wrap=False),
                ft.Text(value="Tovar nomi", text_align="left", width=150, weight="bold", no_wrap=False),
                ft.Text(value="Bor soni", text_align="left", width=100, weight="bold", no_wrap=False),
                ft.Text(value="Narxi", text_align="left", width=100, weight="bold", no_wrap=False)
            ]),
            ft.Row(controls=[
                bc_out,
                name_out,
                qtty_out,
                cost_out
            ])
        ])
    )
    checkout_container = ft.Container(
        width=1200,
        padding=20,
        content=ft.Row(controls=[
            ft.Column(controls=[
                ft.Row(controls=[
                    bcode_field,
                    conf_text
                ]),
                ft.Row(controls=[
                    ft.Container(
                        width=100,
                        padding = 10,
                        margin = 0,
                        border_radius=ft.border_radius.all(10),
                        border=ft.border.all(1, "#09E109"),
                        content=ft.Text(value='№', weight='bold', size= 20, text_align='center')
                    ),
                    ft.Container(
                        width=350,
                        padding = 10,
                        margin = 0,
                        border_radius=ft.border_radius.all(10),
                        border=ft.border.all(1, "#09E109"),
                        content=ft.Text(value='Tovar Nomi', weight='bold', size= 20, text_align='center')
                    ),
                    ft.Container(
                        width=100,
                        padding = 10,
                        margin = 0,
                        border_radius=ft.border_radius.all(10),
                        border=ft.border.all(1, "#09E109"),
                        content=ft.Text(value='Soni', weight='bold', size= 20, text_align='center')
                    ),
                    ft.Container(
                        width=250,
                        padding = 10,
                        margin = 0,
                        border_radius=ft.border_radius.all(10),
                        border=ft.border.all(1, "#09E109"),
                        content=ft.Text(value='Narxi', weight='bold', size= 20, text_align='center')
                    )]),
                ft.Row(controls=[
                    ft.Container(
                        width = 833,
                        border_radius=ft.border_radius.all(10),
                        border=ft.border.all(1, "#09E109"),
                        content=chck_list
                    )]),
                ft.Row(controls=[
                    ft.Container(
                        width=600,
                        margin=0,
                        padding=ft.Padding(30,0,0,0),
                        border_radius=ft.border_radius.all(10),
                        border= ft.border.all(1, "#09E109"),
                        content=ft.Row(controls=[
                            ft.Text(weight='bold', size=24, value='Umumiy narx:'),
                            ft.Container(
                                width=400,
                                padding=20,
                                margin=0,
                                border_radius=ft.border_radius.all(10),
                                border= ft.border.all(1, "#09E109"),
                                content=total_price
                            )
                        ])
                    ),
                    ft.ElevatedButton(content=ft.Container(
                        width=200,
                        padding=20,
                        border_radius=ft.border_radius.all(35),
                        content=ft.Text(weight='bold', size=20, text_align='center', value="To'lash", color="#FFFFFF")
                    ), style=ft.ButtonStyle(bgcolor='#08BF5B', overlay_color='#0DEA61', color='#FFFFFF', elevation=True, surface_tint_color='#EA091C'), on_click=checkout)
                ]),
                ft.Row(controls=[
                    ft.ElevatedButton(text='Raqamsiz tovarlar', on_click=extra_dialog_open)
                ])
            ])
        ])
    )

    extra_items_dialog = ft.AlertDialog(
        title=ft.Text(value='Raqamsiz tovarlar'),
        content=ft.Column(controls=[
        ft.Row(controls=[
            ft.ElevatedButton(text="Bo`lka non", data=1, on_click=add_extra_item),
            ft.ElevatedButton(text="Qora bo`lka", data=2, on_click=add_extra_item),
            ft.ElevatedButton(text="Patir", data=3, on_click=add_extra_item),
        ])
        ])
    )
    
    async def change_page(e):
        #print(e.control.selected_index)
        match e.control.selected_index:
            case 0:
                await page.clean_async()
                bcode_field.on_submit = next_step
                name_field.autofocus = True
                await page.add_async(income_container)
            case 1:
                await page.clean_async()
                bcode_field.on_submit = data_read
                await page.add_async(search_container, output_container)
            case 2:
                await page.clean_async()
                bcode_field.on_submit = add_item
                await page.add_async(checkout_container)
    
    

    nav_income = ft.NavigationDestination(icon=ft.icons.ADD, selected_icon=ft.icons.ADD_OUTLINED,
                                    label="Tovar Kiritish")
    nav_search = ft.NavigationDestination(icon=ft.icons.SEARCH, selected_icon=ft.icons.SEARCH_OUTLINED,
                                    label="Tovar Qidirish")
    nav_checkout = ft.NavigationDestination(icon=ft.icons.SHOPPING_CART_CHECKOUT, selected_icon=ft.icons.SHOPPING_CART_CHECKOUT_OUTLINED,
                                    label="Xisoblash")

    page.navigation_bar = ft.NavigationBar(
        destinations=[
            nav_income,
            nav_search,
            nav_checkout
        ], selected_index=0, on_change=change_page
    )
    
    await page.add_async(income_container)
ft.app(target=main, name="Register")
