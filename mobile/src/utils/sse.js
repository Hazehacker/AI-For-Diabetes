/**
 * SSE / text-event-stream helper for uni-app.
 *
 * Goal: make mobile端像H5一样可以消费 /chat/stream_with_tts 的 event/data 增量。
 * - H5: fetch + ReadableStream reader
 * - APP-PLUS: plus.net.XMLHttpRequest 通过 onreadystatechange(3)/onprogress 解析 responseText 增量
 * - 其他平台: 降级为 uni.request 等待完整文本后一次性解析
 */
import request, { BASE_URL } from '@/utils/request'

const buildUrl = (path) => (path.startsWith('http') ? path : `${BASE_URL}${path}`)

export const createSSEParser = (handlers = {}) => {
  const onEvent = typeof handlers.onEvent === 'function' ? handlers.onEvent : () => {}
  const onDelta = typeof handlers.onDelta === 'function' ? handlers.onDelta : () => {}
  const onConversationId =
    typeof handlers.onConversationId === 'function' ? handlers.onConversationId : () => {}
  const onDone = typeof handlers.onDone === 'function' ? handlers.onDone : () => {}

  const state = {
    currentEvent: null,
    buffer: ''
  }

  const feed = (chunkText) => {
    if (!chunkText) return
    state.buffer += String(chunkText)

    const lines = state.buffer.split('\n')
    state.buffer = lines.pop() || ''

    for (const rawLine of lines) {
      const line = rawLine.trim()
      if (!line) continue

      if (line.startsWith('event:')) {
        state.currentEvent = line.substring(6).trim()
        onEvent(state.currentEvent)
        continue
      }

      if (line.startsWith('data:')) {
        const dataStr = line.substring(5).trim()
        if (!dataStr || dataStr === '[DONE]') continue
        try {
          const data = JSON.parse(dataStr)

          // 有些实现会把 event/type 放在 data 里（而不是 event: 行）
          const inferredEvent =
            state.currentEvent ||
            data?.event ||
            data?.type ||
            data?.event_type ||
            data?.eventName ||
            null
          if (inferredEvent && inferredEvent !== state.currentEvent) {
            state.currentEvent = inferredEvent
            onEvent(state.currentEvent)
          }

          // conversation_id 可能在任意事件里出现
          if (data?.conversation_id) onConversationId(data.conversation_id)

          // 1) 文本增量：最常见字段是 content
          if (typeof data?.content === 'string' && data.content) {
            const ev = state.currentEvent
            const looksLikeDelta =
              !ev || String(ev).includes('delta') || String(ev).includes('message') || String(ev).includes('conversation')
            if (looksLikeDelta) onDelta(data.content, data, ev || 'content')
          }

          // 2) 一次性结果：有些服务端直接给 response 字段（非增量）
          if (typeof data?.response === 'string' && data.response) {
            onDelta(data.response, data, state.currentEvent || 'response')
            onDone(data, state.currentEvent || 'response')
          }

          // follow_up 表示回复完成（H5 端就是靠它 break）
          const evStr = String(state.currentEvent || '')
          const isDoneEvent =
            evStr.includes('follow_up') ||
            evStr.includes('completed') ||
            evStr.includes('done') ||
            data?.done === true ||
            data?.finish === true ||
            data?.is_end === true

          if (isDoneEvent) onDone(data, state.currentEvent || 'done')
        } catch (e) {
          // ignore parse error (可能遇到非JSON行)
        }
      }
    }
  }

  const flush = () => {
    // 把最后残留 buffer 当成一行处理（尽力）
    if (!state.buffer) return
    feed('\n')
  }

  return { feed, flush }
}

/**
 * Stream SSE from backend.
 * @param {object} opts
 * @param {string} opts.path - like '/chat/stream_with_tts'
 * @param {object} opts.body - request json body
 * @param {object} opts.handlers - { onEvent, onDelta, onConversationId, onDone }
 * @returns {Promise<{ text: string }>} - final accumulated text
 */
export const streamSSE = async ({ path, body, handlers = {} }) => {
  const token = uni.getStorageSync('api_token')
  const url = buildUrl(path)

  let fullText = ''
  const parser = createSSEParser({
    ...handlers,
    onDelta: (delta, data, ev) => {
      fullText += delta || ''
      handlers?.onDelta?.(delta, data, ev)
    }
  })

  // ========== H5: fetch stream ==========
  // #ifdef H5
  const controller = new AbortController()
  try {
    const res = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...(token ? { Authorization: `Bearer ${token}` } : {})
      },
      body: JSON.stringify(body || {}),
      signal: controller.signal
    })

    if (!res.ok) throw new Error(`HTTP ${res.status}`)
    const reader = res.body?.getReader?.()
    if (!reader) throw new Error('ReadableStream not supported')
    const decoder = new TextDecoder()

    while (true) {
      const { done, value } = await reader.read()
      if (done) break
      parser.feed(decoder.decode(value, { stream: true }))
    }
    parser.flush()
    return { text: fullText }
  } finally {
    controller.abort()
  }
  // #endif

  // ========== APP-PLUS: xhr incremental ==========
  // #ifdef APP-PLUS
  await new Promise((resolve, reject) => {
    try {
      const xhr = new plus.net.XMLHttpRequest()
      let lastLen = 0

      xhr.onreadystatechange = () => {
        // readyState 3: receiving (partial)
        if (xhr.readyState === 3 || xhr.readyState === 4) {
          const text = xhr.responseText || ''
          const inc = text.substring(lastLen)
          lastLen = text.length
          parser.feed(inc)
        }

        if (xhr.readyState === 4) {
          if (xhr.status >= 200 && xhr.status < 300) {
            parser.flush()
            resolve()
          } else {
            reject(new Error(`HTTP ${xhr.status}`))
          }
        }
      }

      xhr.open('POST', url)
      xhr.setRequestHeader('Content-Type', 'application/json')
      if (token) xhr.setRequestHeader('Authorization', `Bearer ${token}`)
      xhr.send(JSON.stringify(body || {}))
    } catch (e) {
      reject(e)
    }
  })
  return { text: fullText }
  // #endif

  // ========== Other platforms: fallback (wait full, parse once) ==========
  const res = await request({
    url: path,
    method: 'POST',
    data: body || {},
    // 尽量避免 uni 自动按 JSON 解析导致失败
    dataType: 'text',
    timeout: 60000
  })

  // 可能返回 string(SSE文本) 或 object(JSON)
  if (typeof res === 'string') {
    parser.feed(res + '\n')
    parser.flush()
    return { text: fullText || '' }
  }

  // JSON 兜底：兼容 {response} / {data:{response}}
  const text = res?.response ?? res?.data?.response ?? ''
  if (text) {
    fullText = String(text)
    handlers?.onDelta?.(fullText, res, 'json')
  }
  return { text: fullText }
}


