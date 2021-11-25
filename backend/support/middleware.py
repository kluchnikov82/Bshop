def primer(get_response):
    def middleware(request):
        print('До')
        response = get_response(request)
        print('После')
        return response
    return middleware
