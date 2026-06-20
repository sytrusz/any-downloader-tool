import flet as ft
from ui.app import main_app
import uvicorn

# Fix for uvicorn 0.23.2 compatibility with flet
old_init = uvicorn.Config.__init__
def new_init(self, *args, **kwargs):
    if kwargs.get('ws') == 'websockets-sansio':
        kwargs['ws'] = 'auto'
    old_init(self, *args, **kwargs)
uvicorn.Config.__init__ = new_init

if __name__ == '__main__':
    port = 8080
    print(f"\n==============================================")
    print(f"App is running at: http://127.0.0.1:{port}")
    print(f"If your browser didn't open automatically,")
    print(f"hold CTRL and click the link above!")
    print(f"==============================================\n")
    ft.run(main_app, view=ft.AppView.WEB_BROWSER, port=port)
