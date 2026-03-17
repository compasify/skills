# Parsing Workflow Details

## HTML Table Structure

Weekly report pages contain HTML tables with:
- **Columns**: Thứ 2 → Thứ 6 (Monday–Friday), optional "Tổng kết" (Summary)
- **Rows per person**: Two rows — actual work done + plan for next day
- **Sections**: Multiple tables grouped by team (Team Test, Design & BA, dev teams)
- **Row labels**: Person names in `<td><strong>Name</strong></td>` cells
- **Plan rows**: First cell contains "Plan"

## Extraction Rules

From ALL tables, extract:
1. **Work done**: All non-"Plan" rows — actual completed work each day
2. **Plans for next week**: Last "Plan" column entries (Thứ 5/Thứ 6) + "Tổng kết" entries

## Functional Categories

Group work items into:
- **Crawl**: Crawling infra, new platforms, account management, proxy
- **Smart Analysis (SA)**: Profile display, add match, bookmark/note, media
- **Smart Monitor (SM)**: Keywords, violations, filtering
- **Smart Data / Entity**: Data lake, job management, entity detail
- **Report**: Export, queue, status management
- **Notification**: Alerts, socket, real-time updates
- **Base/Auth/Infrastructure**: Backend architecture, auth service, new project setup
- **Design/BA**: UI design, specs, BA tasks

## Deduplication Rules

- DEDUPLICATE: Same bug/feature across multiple days/people → mention ONCE
- MERGE related items: e.g. "fix tên null" + "fix suggestion thiếu tên" → combine
- REMOVE person names — output is anonymous
- REMOVE Redmine ticket numbers (refs #xxxxx)
- REMOVE status transitions (checking → fixed → merged) — state final outcome only
- KEEP technical specifics (platform names, feature names, error types)

## Next Week Plan Sources

1. Explicit "Plan" rows in last workday columns (Thứ 5/Thứ 6)
2. Items marked "đợi" (waiting), "tiếp tục" (continuing), "cần plan" (needs planning)
3. Unresolved issues mentioned in last days
4. BA/Design work in progress with percentage < 100%

## Formatting Rules

- NO markdown formatting (no bold, no headers with #, no links)
- NO person names, NO ticket/issue numbers
- Plain dash (-) for bullet points
- Vietnamese language
- Each bullet: 1 line, concise but specific
- Group related fixes into single bullets (e.g. multiple SM keyword fixes → one bullet)
- Maximum ~15-20 bullets per section — merge aggressively if more
- Include bug count trend if total bug numbers available across the week

## Example Output

```
CÔNG VIỆC ĐÃ LÀM TUẦN NÀY

- Hoàn thành BE logic multiple crawl profile (Kafka pub/sub), test ổn định
- Code login Threads xong, crawl main info + following
- Update code hạn chế die account Instagram (bỏ reply comment, tăng delay, set limit ~50)
- Fix video download YouTube/TikTok không mở được
- Fix Smart Monitor: count từ khóa, highlight từ khóa mới, lọc bài post vi phạm, lỗi 500 ký tự đặc biệt
- Fix Smart Data: hiển thị sai profile, không search darkweb, thiếu tin nhắn Telegram
- Fix notification job Smart Data, đồng bộ status real-time
- Test report Smart Monitor, xử lý status khi downtime, handle limit exec report
- Update Base Backend Clean Architecture/DDD, thêm Auth service
- Design Add Multiple Targets, Dashboard Health Check (~40%)
- Tổng bug: 44 đầu tuần, giảm còn 37 cuối tuần


KẾ HOẠCH TUẦN TỚI

- Tiếp tục fix bug Redmine toàn team
- Implement UI Multiple Crawl
- Crawl followers + posts Threads
- Fix triệt để Report: queue, status, cơ chế restart server
- BA limitation report và import
- Tiếp tục design Dashboard Health Check
- Check healthy account/proxy Instagram
```
