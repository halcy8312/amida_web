from app import create_app
import logging

# アプリケーションのインスタンス化
app = create_app()

if __name__ == '__main__':
    # ログ設定
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s')
    app.logger.setLevel(logging.DEBUG)
    app.logger.debug('Starting application with Waitress')

    from waitress import serve
    serve(app, host='0.0.0.0', port=8080)
