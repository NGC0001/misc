var najax = require('najax');
var jimp = require('jimp');


// For javascript Promise, refer to
// https://www.promisejs.org/implementing/

// https://mp.weixin.qq.com/
// https://git.weixin.qq.com/users/perfect_information


var serverProtocol = 'http://';
var serverName = 'yjcx.ems.com.cn';
var serverUrl = serverProtocol + serverName;  // http://yjcx.ems.com.cn


dataObj = {
    'serverUrl': serverUrl,
    'htmlUrl': serverUrl + '/qps/yjcx',  // http://yjcx.ems.com.cn/qps/yjcx
    'versityUrl': serverUrl + '/qps/qpswaybilltraceOutinternal/versity',
    'captchaGetUrl': serverUrl + '/qps/showPicture/verify/slideVerifyLoad',
    'captchaValidateUrl': serverUrl + '/qps/showPicture/verify/slideVerifyCheck',
};


get_html(dataObj);


function error_handler(err) {
    console.log('Error:', err);
}


function get_html(dataObj) {
    najax({
        type: 'GET',
        url: dataObj.htmlUrl,
        beforeSend: xhr => {
            xhr.setRequestHeader('Connection', 'keep-alive');
        },
    })
    .done((htmlData, status, xhr) => {
        // console.log(status, xhr.getAllResponseHeaders());
        dataObj.cookie = xhr.getResponseHeader('Set-Cookie')[0].split(';')[0];
        // console.log('dataObj.cookie', dataObj.cookie);
        get_slide_captcha(dataObj);
    })
    .fail(error_handler);
}


function get_slide_captcha(dataObj) {
    najax({
        type: 'GET',
        url: dataObj.captchaGetUrl + '?t=' + new Date().getTime(),
        beforeSend: xhr => {
            xhr.setRequestHeader('Connection', 'keep-alive');
            xhr.setRequestHeader('Cookie', dataObj.cookie);
            xhr.setRequestHeader('Referer', dataObj.htmlUrl);
        },
        data: {},
        dataType: "json",
    })
    .done((captchaData, status, xhr) => {
        dataObj.captchaData = captchaData;
        check_retrieved_captcha_image(dataObj);
    })
    .fail(error_handler);
}


function check_retrieved_captcha_image(dataObj) {
    return new Promise(resolve => {
        resolve(dataObj);
    })
    .then(dataObj => {
        // _test_manipulate_base64_image(dataObj.captchaData.CutPng_base64, 'patch');
        // _test_manipulate_base64_image(dataObj.captchaData.YYPng_base64, 'full');
        return dataObj;
    })
    .then(find_patch_outline)
    .catch(error_handler);
}


function find_patch_outline(dataObj) {
    return jimp.read(Buffer.from(dataObj.captchaData.CutPng_base64, 'base64'))
    .then(image => {
        for (let x = 0; x < image.bitmap.width; x++) {
            for (let y = 0; y < image.bitmap.height; y++) {
                var color = image.getPixelColor(x, y);
                if ((color & 0x000000FF) == 0xFF) {
                    var outline = [];
                    // Directions: Down:0, Right:1, Up:2, Left:3 .
                    var dp = 0;
                    var xp = x;
                    var yp = y;
                    do {
                        outline.push({xp, yp});
                        var dn = (dp + 1) % 4;
                        for(; dn != (dp+2)%4; dn = (dn+3)%4) {
                            let xn = xp + (2 - dn) % 2;
                            let yn = yp + (1 - dn) % 2;
                            if (xn >= 0 && xn < image.bitmap.width
                                && yn >= 0 && yn < image.bitmap.height) {
                                let cn = image.getPixelColor(xn, yn);
                                if ((cn & 0x000000FF) == 0xFF) {
                                    xp = xn;
                                    yp = yn;
                                    break;
                                }
                            }
                        }
                        dp = dn;
                    } while ((xp != x) || (yp != y));
                    dataObj.patchImage = image;
                    dataObj.patchLine = {x, y, outline};
                    return dataObj;
                }
            }
        }
        throw new Error('Failed_To_Find_Outline');
    })
    .then(check_path_outline)
    .catch(error_handler);
}


function check_path_outline(dataObj) {
    return new Promise(resolve => {
        resolve(dataObj);
    })
    .then(dataObj => {
        // _draw_patch_outline(dataObj.patchImage, dataObj.patchLine);
        return dataObj;
    })
    .then(fit_patch_onto_full_image)
    .catch(error_handler);
}


function fit_patch_onto_full_image(dataObj) {
    return jimp.read(Buffer.from(dataObj.captchaData.YYPng_base64, 'base64'))
    .then(image => {
        for (let x = 0; x < image.bitmap.width; x++) {
            for (let y = 0; y < image.bitmap.height; y++) {
                var color = image.getPixelColor(x, y);
                if (color == 0xFFFFFFFF) {
                    var fit = true;
                    var patchLine = dataObj.patchLine;
                    patchLine.outline.forEach(p => {
                        let xn = x + p.xp - patchLine.x;
                        let yn = y + p.yp - patchLine.y;
                        if (xn >= 0 && xn < image.bitmap.width
                            && yn >= 0 && yn < image.bitmap.height) {
                            let cn = image.getPixelColor(xn, yn);
                            if (cn == 0xFFFFFFFF) {
                                return;
                            }
                        }
                        fit = false;
                    });
                    if (fit) {
                        dataObj.fullImage = image;
                        dataObj.fitPos = {x, y};
                        dataObj.fitMove = {x: x - patchLine.x, y: y - patchLine.y};
                        return dataObj;
                    }
                }
            }
        }
        throw new Error('Failed_To_Patch_Image');
    })
    .then(query_for_result)
    .catch(error_handler);
}


function query_for_result(dataObj) {
    // console.log(dataObj.captchaData.uuid, dataObj.fitPos.x, dataObj.patchLine.x, dataObj.fitMove.x);
    najax({
        type: "POST",
        url: dataObj.captchaValidateUrl,
        beforeSend: xhr => {
            xhr.setRequestHeader('Connection', 'keep-alive');
            xhr.setRequestHeader('Cookie', dataObj.cookie);
            xhr.setRequestHeader('Referer', dataObj.htmlUrl);
            xhr.setRequestHeader('Origin', dataObj.serverUrl);
        },
        data: {
            uuid: dataObj.captchaData.uuid,
            moveEnd_X: parseInt(dataObj.fitMove.x),
            'text[]': '1234567890',  // TODO: Array does not work. (Indices attached by najax)
            selectType: '1',
        },
        dataType: "json",
    })
    .then((queryResData, status, xhr) => {
        dataObj.queryResData = queryResData;
        process_query_result(dataObj);
    })
    .fail(error_handler);
}


function process_query_result(dataObj) {
    var queryResData = dataObj.queryResData;
    console.log('queryResData.YZ', queryResData.YZ);
    if (queryResData.YZ == "no") {
        console.log("验证失败");
    } else if (queryResData.YZ == "noSession") {
        console.log("图片验证码已失效");
    } else if (queryResData.YZ == "noAccess") {
        console.log("当前邮件包含70、71开头的平信邮件,暂不支持查询!");
    } else if (queryResData.YZ == "unnormal") {
        console.log("服务器繁忙,请刷新后重试!");
    } else {
        console.log(queryResData);
    }
    return dataObj;
}


// ###########################


function _test_manipulate_base64_image(base64Image, imgName) {
    imgBuf = Buffer.from(base64Image, 'base64');
    jimp.read(imgBuf, (err, image) => {
        if (err) throw err;

        image.write(imgName + '.' + image.getExtension());

        var printImage = false;
        if (printImage) {
            image.scan(0, 0, image.bitmap.width, image.bitmap.height, function(x, y, idx) {
                // x, y is the position of this pixel on the image
                // idx is the position start position of this rgba tuple in the bitmap Buffer
                // this is the image
                var red = this.bitmap.data[idx + 0];
                var green = this.bitmap.data[idx + 1];
                var blue = this.bitmap.data[idx + 2];
                var alpha = this.bitmap.data[idx + 3];
                // rgba values run from 0 - 255
                // e.g. this.bitmap.data[idx] = 0; // removes red from this pixel
            });
            for (let y = 0; y < image.bitmap.height; y++) {
                for (let x = 0; x < image.bitmap.width; x++) {
                    var color = image.getPixelColor(x, y);
                    var idx = image.getPixelIndex(x, y);
                    var red = image.bitmap.data[idx + 0];
                    var green = image.bitmap.data[idx + 1];
                    var blue = image.bitmap.data[idx + 2];
                    var alpha = image.bitmap.data[idx + 3];
                    if ((color == 0xFFFFFFFF) || ((color & 0x000000FF) == 0)) {
                        process.stdout.write(1 + '');
                    } else {
                        process.stdout.write(0 + '');
                    }
                    // x += 2;
                }
                process.stdout.write('\n');
            }
        }

        process.stdout.write(
            '  A test for ANSI escape sequence.'
            + '\033[34m\033[s\033[0G>\033[u\033[0m <\n'
        );
        console.log('image:'+imgName, image.hasAlpha(),
            'width='+image.bitmap.width, 'height='+image.bitmap.height);
    });
}


function _draw_patch_outline(image, patchLine) {
    for (let y = 0; y < image.bitmap.height; y++) {
        for (let x = 0; x < image.bitmap.width; x++) {
            var include = false;
            patchLine.outline.forEach(p => {
                if (x == p.xp && y == p.yp) include = true;
            });
            if (include) {
                process.stdout.write('0');
            } else {
                process.stdout.write('1');
            }
        }
        console.log();
    }
    console.log(patchLine.x, patchLine.y);
}
