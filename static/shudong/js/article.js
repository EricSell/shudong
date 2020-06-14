// $(function () {
//     $('.article').click(function () {
//         let id = $(this).attr("a_id");
//
//         $.ajax({
//             type: "GET",
//             url: "/api/article/",
//             async: true,
//             data: {'id': id},// 参数
//
//             success: (function (res) {
//                 temp = '';
//                 for (var i = 0; i < res.article_list.length; i++) {
//                     a = res.article_list[i];
//                     temp += `<li><i><a href="/info/${a.article_id}"><img src="${a.article_img}"></a></i> <h3><a href="/info/${a.article_id}">${a.article_name}</a></h3><p>${a.article_content}</p></li>`
//                 }
//                 $('.r_box').html(temp)
//             }),
//
//             error: (function (e) {
//                 console.log(e)
//             })
//         })
//     });
//
//
// });
