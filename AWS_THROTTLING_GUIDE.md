# AWS Bedrock Throttling - Complete Fix Guide

## 🚨 Problem
AWS Bedrock has rate limits (requests per minute/second) that can cause `ThrottlingException` errors when agents make API calls too quickly:
```
ThrottlingException: Too many requests, please wait before trying again.
```

## ✅ Solutions Implemented

### 1. **Automatic Retry with Exponential Backoff** (Built-in)
The `BedrockClient` now automatically retries failed requests with exponential backoff.

**How it works:**
- First attempt: Immediate
- Retry 1: Wait 2 seconds
- Retry 2: Wait 4 seconds
- Retry 3: Wait 8 seconds
- Retry 4: Wait 16 seconds
- Retry 5: Wait 32 seconds

**Configuration:**
- Default: 5 retries (max 62 seconds total wait)
- No configuration needed - works automatically!

**Logs to watch for:**
```
⚠️ Throttled by AWS Bedrock (attempt 1/5). Retrying in 2s...
✅ Successfully invoked after 2 attempts
```

---

### 2. **Agent Invocation Delay** (Configurable)
Adds a delay between agent invocations to prevent rapid-fire API calls.

**How to configure:**
Add to `backend/.env`:
```bash
# Delay between agent invocations (seconds)
AGENT_INVOCATION_DELAY=2
```

**Recommended values:**
- **Standard AWS account**: `2-3` seconds
- **Higher quota account**: `1` second
- **Testing/debugging**: `0` (no delay, but expect throttling)
- **Conservative (avoid throttling)**: `5` seconds

**Trade-offs:**
- ⚡ Lower delay = Faster research, more throttling risk
- 🐢 Higher delay = Slower research, no throttling

**Example calculations** (1 iteration with 5 agents):
- Delay = 0s → ~30 seconds total
- Delay = 2s → ~40 seconds total (8s added)
- Delay = 5s → ~55 seconds total (20s added)

---

### 3. **Request AWS Quota Increase** (Long-term solution)

#### Check Your Current Quotas
```bash
# Install AWS CLI if not installed
pip install awscli

# View your current Bedrock quotas
aws service-quotas list-service-quotas \
  --service-code bedrock \
  --region us-east-1
```

#### Request Quota Increase
1. Go to [AWS Service Quotas Console](https://console.aws.amazon.com/servicequotas/)
2. Select **Amazon Bedrock**
3. Find these quotas:
   - **"Rate of on-demand requests per model"**
   - **"Burst rate of on-demand requests per model"**
4. Click **Request quota increase**
5. Enter desired value (e.g., increase from 10 to 50 requests/minute)
6. Submit with justification: "Running multi-agent research system that makes sequential API calls"

**Typical approval time:** 1-3 business days

---

## 🔧 Quick Configuration Examples

### Scenario 1: **Development/Testing**
You want fast iteration and don't mind occasional throttling:

```bash
# backend/.env
AGENT_INVOCATION_DELAY=1
MAX_ITERATIONS=1
```

### Scenario 2: **Production - Standard Account**
Balanced speed and reliability:

```bash
# backend/.env
AGENT_INVOCATION_DELAY=2
MAX_ITERATIONS=3
```

### Scenario 3: **Production - High Quota**
Fast and reliable (after AWS quota increase):

```bash
# backend/.env
AGENT_INVOCATION_DELAY=0.5
MAX_ITERATIONS=5
```

### Scenario 4: **Conservative (Guarantee No Throttling)**
Slower but zero throttling risk:

```bash
# backend/.env
AGENT_INVOCATION_DELAY=5
MAX_ITERATIONS=3
```

---

## 📊 Monitoring Throttling

### Check Backend Logs
```bash
# View live logs
tail -f backend/backend.log

# Search for throttling
grep "Throttled" backend/backend.log

# Count throttling events
grep -c "Throttled" backend/backend.log
```

### What to Look For
**Good (working well):**
```
✅ Successfully invoked after 1 attempts
Tokens used: 1234 input, 567 output
```

**Warning (retrying):**
```
⚠️ Throttled by AWS Bedrock (attempt 1/5). Retrying in 2s...
✅ Successfully invoked after 2 attempts
```

**Critical (all retries exhausted):**
```
⚠️ Throttled by AWS Bedrock (attempt 5/5). Retrying in 32s...
ERROR: AWS ClientError (ThrottlingException): ...
```

---

## 🎯 Recommended Setup

1. **Start with defaults** (built-in):
   - Automatic retry: ✅ Enabled
   - Agent delay: `2` seconds

2. **Monitor your first few research runs**:
   ```bash
   tail -f backend/backend.log | grep -E "Throttled|Successfully"
   ```

3. **Adjust based on results**:
   - **No throttling seen?** → Reduce `AGENT_INVOCATION_DELAY` to `1`
   - **Occasional throttling (1-2 retries)?** → Keep at `2`
   - **Frequent throttling (3+ retries)?** → Increase to `3-5`
   - **Max retries exceeded?** → Increase to `5` AND request AWS quota increase

---

## 🚀 Advanced: Multiple Bedrock Accounts/Regions

If you need higher throughput, distribute across multiple accounts or regions:

```python
# backend/flux_core/tools/bedrock_client.py
# Rotate between multiple profiles
AWS_PROFILES = ["default", "research-account-2", "research-account-3"]
current_profile_idx = 0

def get_next_client():
    global current_profile_idx
    profile = AWS_PROFILES[current_profile_idx]
    current_profile_idx = (current_profile_idx + 1) % len(AWS_PROFILES)
    return BedrockClient(profile_name=profile)
```

---

## ❓ FAQ

### Q: Why am I still seeing throttling with retry enabled?
**A:** Retries handle individual request failures. If you're making 10 requests in rapid succession, all 10 might get throttled initially. The `AGENT_INVOCATION_DELAY` prevents this.

### Q: Can I disable retries?
**A:** Not recommended, but you can modify `bedrock_client.py` and set `max_retries=1`.

### Q: Does throttling cost money?
**A:** No. Throttled requests don't consume tokens or cost anything. Only successful requests are billed.

### Q: What's the default AWS Bedrock quota?
**A:** Varies by account type and region, typically:
- **On-Demand**: 10-50 requests/minute per model
- **Burst**: 2-10 requests/second (short bursts)

### Q: How do I check my actual quota?
```bash
aws service-quotas get-service-quota \
  --service-code bedrock \
  --quota-code L-xxxxxxxx \  # Get code from list-service-quotas
  --region us-east-1
```

---

## 📝 Summary Checklist

- [x] Automatic retry with exponential backoff: **Built-in** ✅
- [ ] Set `AGENT_INVOCATION_DELAY` in `backend/.env`: **Configure**
- [ ] Monitor logs for throttling events: **Observe**
- [ ] Request AWS quota increase if needed: **Long-term fix**

**Most users won't need to do anything** - the default retry logic handles occasional throttling automatically! 🎉

---

## 🔗 Resources
- [AWS Bedrock Quotas Documentation](https://docs.aws.amazon.com/bedrock/latest/userguide/quotas.html)
- [AWS Service Quotas Console](https://console.aws.amazon.com/servicequotas/)
- [AWS Bedrock Pricing](https://aws.amazon.com/bedrock/pricing/)

