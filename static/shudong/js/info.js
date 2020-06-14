$(function () {
    $('#forminput').click(function () {
        let captcha = $('.capt').html();
        let user_capt = $('#inputcapt').val();

        if (String(captcha) === String(user_capt)) {
            let id = $('.capt').attr('a_id');
            let name = $('#username').val().trim();
            let command = $('#command').val();
            if (name != "" && name.length <= 8) {
                if (command != "") {
                    $.ajax({
                        type: "GET",
                        url: '/command',
                        async: true,
                        data: {
                            'id': id,
                            'name': name,
                            'command': command,
                        },
                        success: (function (res) {
                            // alert(res)
                            // alert($('.commandlist:last-child').next())
                            $('#commandlist').append(` <div class="fb" ><ul id="commandlist"><p class=\"fbtime\"><span>${res.time}</span>${res.name}</p><p class=\"fbinfo\">${res.commands}</p></ul></div>`)
                            $('#username').val("")
                            $('#inputcapt').val("")
                            $('#command').val("")
                            get_capt()
                        }),
                        error: (function (res) {
                            console.log(res)
                        })
                    })
                } else {
                    alert("评论不能为空")
                }

            } else {
                alert("用户名长度小于8位或为空")
            }
        } else {
            alert("验证码输入不正确")
        }
    });

    // 更改验证码
    $('.capt').click(function () {
        get_capt()
    })

    // 获取验证码函数
    function get_capt() {
        that = $('.capt');
        $.ajax({
            type: 'POST',
            url: '/api/change_captcha/',
            data: {},
            success: function (res) {
                that.html(res.captchas)
            },
            error: function (e) {
                console.log(e)
            }
        })
    }
})

