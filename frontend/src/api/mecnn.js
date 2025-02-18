import req from '@/libs/api.request'

// 智能预警
// 文件上传
export const eqcnn = (data) => {
  return req.axios2.request({
    url: '/mecnn/eqcnn',
    data: data,
    method: 'POST'
  })
}
// 获取上传的文件列表
export const show = (data) => {
  return req.axios2.request({
    url: '/mecnn/show',
    params: data,
    method: 'GET'
  })
}
// 预警信息 hist_magpre
export const hist_magpre = (data) => {
  return req.axios2.request({
    url: '/mecnn/hist_magpre',
    params: data,
    method: 'POST'
  })
}