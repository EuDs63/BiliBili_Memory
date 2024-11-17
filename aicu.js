// 从 URL 的查询部分解析 uid 和 pn 参数

const urlParams = new URLSearchParams(window.location.search);
const uid = urlParams.get('uid') || '';
const pn = parseInt(urlParams.get('pn')) || 1;
const ps = 100;
var timeoutId; // 声明在全局作用域内
var uidqj;
document.getElementById('filterSelect').select('0');

// 初始化页面
fetchData(uid, pn, ps, "", 0, false);
getuserinfo(uid, false);


linkCard('link', uid);
setcolor(getcolor());

function handleFilterChange() {
    var searchValue = document.getElementById('searchInput').value;
    var filterIndex = document.getElementById('filterSelect').value;
    fetchData(uid, 1, ps, searchValue, filterIndex, false);
}
function triggerFetch() {
    var searchValue = document.getElementById('searchInput').value;
    var filterIndex = document.getElementById('filterSelect').value;
    fetchData(uid, 1, ps, searchValue, filterIndex, false);
}
function fetchData(uid, pn, ps, kw, mode, move) {
    // 在发起请求前显示加载动画和灰色蒙层
    showLoader();

    // var url = `http://127.0.0.1:8080/api/v3/search/getreply?uid=${uid}&pn=${pn}&ps=${ps}&mode=${mode}&keyword=${kw}`
    var url = apiurl() + `/api/v3/search/getreply?uid=${uid}&pn=${pn}&ps=${ps}&mode=${mode}&keyword=${kw}`
    fetch(url,{credentials: 'include'})
        .then(response => response.json())
        .then(data => {

                uidqj = uid;
                if (data.code === 0) {
                    // 更新显示count的元素内容
                    const countElement = document.getElementById('count');
                    countElement.innerText = "评论数 " + data.data.cursor.all_count;

                    const contentDiv = document.getElementById('content');
                    contentDiv.innerHTML = '';

                    data.data.replies.forEach(item => {
                        const cardDiv = document.createElement('div');
                        cardDiv.className = 'card';

                        const timeDiv = document.createElement('div');
                        timeDiv.className = 'time';
                        timeDiv.innerText = new Date(item.time * 1000).toLocaleString() + ' ' + item.rank;
                        cardDiv.appendChild(timeDiv);

                        const messageDiv = document.createElement('div');
                        messageDiv.className = 'message';
                        messageDiv.style.whiteSpace = 'pre-wrap';  // 让换行符起作用
                        messageDiv.innerHTML = escapeRegExp(item.message);
                        cardDiv.appendChild(messageDiv);

                        const zDiv = document.createElement('div');
                        zDiv.className = 'z';
                        zDiv.innerText = "当前查询uid:" + uid + " 爱来自aicu.cc";
                        cardDiv.appendChild(zDiv);

                        const buttonsDiv = document.createElement('div');
                        buttonsDiv.className = 'buttons';
                        buttonsDiv.setAttribute('style', 'justify-content: flex-end;');

                        const button0 = document.createElement('md-filled-button');
                        button0.textContent = '方式0';
                        let url0;
                        switch (item.dyn.type) {
                            case 17:
                                url0 = `https://t.bilibili.com/${item.dyn.oid}#reply${item.rpid}`;
                                break;
                            case 1:
                                url0 = `https://www.bilibili.com/video/av${item.dyn.oid}#reply${item.rpid}`;
                                break;
                            case 12:
                                url0 = `https://www.bilibili.com/read/cv${item.dyn.oid}#reply${item.rpid}`;
                                break;
                            default:
                                url0 = `https://t.bilibili.com/${item.dyn.oid}?type=${zhtype(item.dyn.type)}#reply${item.rpid}`;
                                break;
                        }
                        button0.href = url0;
                        button0.target = '_blank'; // 在新的一页中打开
                        buttonsDiv.appendChild(button0);

                        const button2 = document.createElement('md-filled-button');
                        button2.textContent = '方式2';

                        let url2;
                        if (item.rank == 1) {
                            url2 = 'https://www.bilibili.com/h5/comment/sub?oid=' + item.dyn.oid + '&pageType=' + item.dyn.type + '&root=' + item.rpid;
                        } else {
                            url2 = 'https://www.bilibili.com/h5/comment/sub?oid=' + item.dyn.oid + '&pageType=' + item.dyn.type + '&root=' + item.parent.rootid;
                        }

                        button2.href = url2;
                        button2.target = '_blank'; // 在新的一页中打开
                        buttonsDiv.appendChild(button2);

                        if (checkAppInstalled("bilibili://")) { // 当前设备是移动设备
                            const button3 = document.createElement('md-filled-tonal-button');
                            button3.textContent = '方式3';
                            let url3;
                            if (item.dyn.type == 17) {
                                url3 = 'bilibili://comment/detail/' + item.dyn.type + '/' + item.dyn.oid + '/' + item.rpid + '/?subType=0&anchor=' + item.rpid + '&showEnter=1&extraIntentId=0&scene=1&enterName=查看动态 爱来自aicu.cc&title=你所热爱的就是你的生活&enterUri=https://t.bilibili.com/' + item.dyn.oid;
                            } if (item.dyn.type == 1) {
                                url3 = 'bilibili://comment/detail/' + item.dyn.type + '/' + item.dyn.oid + '/' + item.rpid + '/?subType=0&anchor=' + item.rpid + '&showEnter=1&extraIntentId=0&scene=1&enterName=查看动态 爱来自aicu.cc&title=你所热爱的就是你的生活&enterUri=https://www.bilibili.com/video/av' + item.dyn.oid;
                            } else {
                                url3 = 'bilibili://comment/detail/' + item.dyn.type + '/' + item.dyn.oid + '/' + item.rpid + '/?subType=0&anchor=' + item.rpid + '&showEnter=1&extraIntentId=0&scene=1&enterName=查看动态 爱来自aicu.cc&title=你所热爱的就是你的生活&enterUri=https://t.bilibili.com/' + item.dyn.oid + '?type=' + zhtype(item.dyn.type);
                            }
                            button3.href = url3;
                            button3.target = '_blank'; // 在新的一页中打开
                            buttonsDiv.appendChild(button3);
                        }

                        cardDiv.appendChild(buttonsDiv);
                        contentDiv.appendChild(cardDiv);

                    });

                    const paginationDiv = document.getElementById('pagination');
                    paginationDiv.innerHTML = '';

                    const maxPage = Math.ceil(data.data.cursor.all_count / ps);
                    const currentPage = pn;

                    const pageButtons = [];

                    if (maxPage <= 10) {
                        for (let i = 1; i <= maxPage; i++) {
                            pageButtons.push(i);
                        }
                    } else {
                        if (currentPage <= 5) {
                            for (let i = 1; i <= 6; i++) {
                                pageButtons.push(i);
                            }
                            pageButtons.push('...');
                            pageButtons.push(maxPage);
                        } else if (currentPage >= maxPage - 4) {
                            pageButtons.push(1);
                            pageButtons.push('...');
                            for (let i = maxPage - 5; i <= maxPage; i++) {
                                pageButtons.push(i);
                            }
                        } else {
                            pageButtons.push(1);
                            pageButtons.push('...');
                            for (let i = currentPage - 2; i <= currentPage + 2; i++) {
                                pageButtons.push(i);
                            }
                            pageButtons.push('...');
                            pageButtons.push(maxPage);
                        }
                    }

                    pageButtons.forEach(button => {
                        const pageButton = document.createElement('a');
                        pageButton.className = 'pagination-button';
                        if (button === '...') {
                            pageButton.innerText = '...';
                            pageButton.disabled = true;
                        } else {
                            pageButton.innerText = button;
                            if (button === currentPage) {
                                pageButton.classList.add('active');
                            }
                        }
                        paginationDiv.appendChild(pageButton);

                        pageButton.addEventListener('click', () => {
                            if (button !== '...') {
                                const urlParams = new URLSearchParams(window.location.search);
                                urlParams.set('pn', button);
                                const newUrl = `${window.location.pathname}?${urlParams.toString()}`;
                                window.history.replaceState(null, null, newUrl); // 使用replaceState替代pushState

                                var searchValue = document.getElementById('searchInput').value;
                                var filterIndex = document.getElementById('filterSelect').value;
                                fetchData(uid, button, ps, searchValue, filterIndex, true);
                            }
                        });
                    });
                    // 请求完成后隐藏加载动画和灰色蒙层
                    hideLoader(move);
                } else {
                    yccl(data.message, 'zb')
                }
            }
        )
        .catch(error => {
            yccl('请求失败，请稍后重试。若长时间没有恢复请联系我们。', error)

        });
}
function yccl(err, error) {
    console.log(error);
    // 请求完成后隐藏加载动画和灰色蒙层
    hideLoader();
    // 添加错误提示卡片
    const countElement = document.getElementById('count');
    countElement.innerText = '请求失败'

    const contentDiv = document.getElementById('content');
    contentDiv.innerHTML = '';
    const cardDiv = document.createElement('div');
    cardDiv.className = 'card';
    const messageDiv = document.createElement('div');
    messageDiv.style.whiteSpace = 'pre-wrap';
    messageDiv.className = 'message';
    messageDiv.innerHTML = err;

    cardDiv.appendChild(messageDiv);
    contentDiv.appendChild(cardDiv);
}