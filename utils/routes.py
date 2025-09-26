from flask import blueprints, send_from_directory, current_app, request, jsonify
from utils.client import Client
from utils.bot import trigger_bot_access
from jwt import decode, encode, ExpiredSignatureError, InvalidTokenError
from utils.security import verify_password
import os
import json
from datetime import datetime
import re

ADMIN_API_ROUTES = blueprints.Blueprint("admin_api_routes", __name__)
PUBLIC_ROUTES = blueprints.Blueprint("user_routes", __name__)
PUBLIC_API_ROUTES = blueprints.Blueprint("user_api_routes", __name__)

PUBLIC_ROUTES.add_url_rule(
    "/", "index", lambda: send_from_directory("templates", "index.html")
)

SCRIPT_PATTERN = re.compile(r"<\s*script[^>]*>|<\s*/\s*script\s*>", re.IGNORECASE)

@ADMIN_API_ROUTES.before_request
def check_admin_access(is_request: bool = True):
    cookie = request.cookies
    token = cookie.get("token")
    if not token:
        if is_request:
            return jsonify({"success": False, "message": "Unauthorized access"}), 401
        else:
            return False

    # 云函数兼容性处理
    try:
        secret_key = current_app.config["SECRET_KEY"]
    except AttributeError:
        secret_key = os.environ.get("SECRET_KEY", "")

    if not secret_key:
        if is_request:
            return (
                jsonify(
                    {
                        "success": False,
                        "message": "Server configuration error: missing secret key.",
                    }
                ),
                500,
            )
        else:
            return False

    try:
        payload = decode(
            token,
            secret_key,  # 使用获取到的secret_key
            algorithms=["HS256"],
        )
        if not is_request:
            return True
    except ExpiredSignatureError:
        if is_request:
            response = jsonify({"success": False, "message": "Token expired"})
            response.delete_cookie("token")
            return response, 401
        else:
            return False
    except InvalidTokenError:
        if is_request:
            response = jsonify({"success": False, "message": "Invalid token"})
            response.delete_cookie("token")
            return response, 401
        else:
            return False
    except Exception as e:
        if is_request:
            response = jsonify(
                {"success": False, "message": f"Error decoding token: {str(e)}"}
            )
            response.delete_cookie("token")
            return (
                response,
                500,
            )
        else:
            return False


@PUBLIC_ROUTES.route("/static/<path:filename>")
def static_files(filename):
    """
    提供静态文件服务，允许访问 static 目录下的静态资源。
    """
    return send_from_directory("static", filename)


@PUBLIC_API_ROUTES.route("/health")
def health_check():
    """
    健康检查接口，返回服务状态。
    """
    return {"status": "ok"}, 200


@PUBLIC_API_ROUTES.route("/items", methods=["GET"])
def get_items():
    """
    获取网站所有者的所有好物的接口
    """
    client: Client = current_app.client

    data = client.load()
    processed_items = []
    for item in data:
        try:
            entry_date_str = item.get("entry_date")
            if not entry_date_str:
                continue
            
            entry_date = datetime.strptime(entry_date_str, "%Y-%m-%d").date()

            retire_date_str = item.get("retire_date")
            retire_date = None
            if retire_date_str:
                retire_date = datetime.strptime(retire_date_str, "%Y-%m-%d").date()

            purchase_price = item.get("purchase_price") or 0.0
            additional_price = item.get("additional_price") or 0.0
            total_price = purchase_price + additional_price

            if retire_date:
                days_in_service = (retire_date - entry_date).days + 1
            else:
                days_in_service = (datetime.now().date() - entry_date).days + 1
            
            daily_price = total_price / days_in_service if days_in_service > 0 else total_price

            processed_items.append({
                "id": item.get("id"),
                "properties": {
                    "物品名称": item.get("name"),
                    "购买价格": item.get("purchase_price"),
                    "附加价值": item.get("additional_price"),
                    "入役日期": item.get("entry_date"),
                    "退役日期": item.get("retire_date"),
                    "服役天数": str(days_in_service) + " 天",
                    "备注": item.get("remark"),
                    "日均价格": str(round(daily_price, 2)) + " 元",
                }
            })
        except (ValueError, TypeError) as e:
            print(f"Skipping item due to error: {e}, item data: {item}")
            continue
    return {"success": True, "items": processed_items, "message": "success"}, 200


@PUBLIC_API_ROUTES.route("/login", methods=["POST"])
def login():
    """
    登录 API
    """
    data = request.json
    username = data.get("username")
    password = data.get("password")
    if not username or not password:
        return (
            jsonify(
                {"success": False, "message": "Username and password are required"}
            ),
            400,
        )

    app_username = current_app.config["WORTHIT_USERNAME"]
    app_password_hash = current_app.config["WORTHIT_PASSWORD"]
    secret_key = current_app.config["SECRET_KEY"]

    if not app_username or not app_password_hash or not secret_key:
        return (
            jsonify(
                {
                    "success": False,
                    "message": "Server configuration error: missing credentials or secret key.",
                }
            ),
            500,
        )

    if username == app_username:
        if verify_password(password, app_password_hash):
            try:
                token = encode(
                    {"username": username},
                    secret_key,  # 使用获取到的secret_key
                    algorithm="HS256",
                )
                response = jsonify({"success": True, "message": "Login successful"})
                response.set_cookie("token", token)
                return response
            except Exception as e:
                # 记录编码token的错误
                current_app.logger.error(f"Error encoding token: {e}")
                return (
                    jsonify({"success": False, "message": "Failed to create token"}),
                    500,
                )
        else:
            return (
                jsonify({"success": False, "message": "Invalid credentials"}),
                401,
            )
    else:
        return jsonify({"success": False, "message": "Invalid credentials"}), 401


@PUBLIC_API_ROUTES.route("/logout", methods=["POST"])
def logout():
    """
    注销 API
    """
    response = jsonify({"success": True, "message": "Logout successful"})
    response.delete_cookie("token")
    return response


@ADMIN_API_ROUTES.route("/health", methods=["GET"])
def admin_health_check():
    """
    检查用户是否登录
    """
    if not check_admin_access(is_request=False):
        return jsonify({"success": False, "message": "Unauthorized access"}), 401
    return jsonify({"success": True, "message": "Admin API is healthy"}), 200


@ADMIN_API_ROUTES.route("/items/<item_id>", methods=["GET"])
def get_item(item_id: str):
    """
    获取指定 ID 的物品数据
    """
    client: Client = current_app.client
    item = None  # 初始化为None
    try:
        item = client.read(item_id)
    except Exception as e:
        return jsonify(
            {
                "success": False,
                "message": "Failed to retrieve item. Please refer to the log for details.",
                "error": str(e),
            }
        )
    if item:
        return (
            jsonify(
                {
                    "success": True,
                    "item": item,
                    "message": "Item retrieved successfully",
                }
            ),
            200,
        )
    else:
        return (
            jsonify(
                {
                    "success": False,
                    "message": "Item not found",
                    "error": "Item not found",
                }
            ),
            404,
        )


@ADMIN_API_ROUTES.route("/items", methods=["POST"])
def create_item():
    """
    创建一个新的物品数据
    """
    client: Client = current_app.client
    data = request.json
    name = data.get("properties", {}).get("name", "")
    entry_date = data.get("properties", {}).get("entry_date")
    purchase_price = data.get("properties", {}).get("purchase_price")
    additional_value = data.get("properties", {}).get("additional_value")
    retirement_date = data.get("properties", {}).get("retirement_date")
    remark = data.get("properties", {}).get("remark", "")
    if SCRIPT_PATTERN.search(name) or SCRIPT_PATTERN.search(remark):
        return jsonify(
            {
                "success": False,
                "message": "Invalid input detected. No script tags allowed.",
            }
        ), 400
    # 检查必填字段
    if not name or not purchase_price:
        return (
            jsonify(
                {
                    "success": False,
                    "message": "Name and purchase price are required fields.",
                }
            ),
            400,
        )
    try:
        result = client.save(
            name=name,
            purchase_price=float(purchase_price),
            additional_price=(
                float(additional_value) if additional_value is not None else 0.0
            ),
            entry_date=entry_date,
            retire_date=retirement_date if retirement_date is not None else None,
            remark=remark if remark is not None else "",
        )
    except Exception as e:
        return jsonify(
            {
                "success": False,
                "message": "Failed to create item. Please refer to the log for details.",
                "error": str(e),
            }
        )
    if result:
        if result:
            return jsonify(
                {
                    "success": True,
                    "message": "Item created successfully.",
                }
            )
        else:
            return (
                jsonify(
                    {
                        "success": False,
                        "message": "Failed to create item. Please refer to the log for details.",
                    }
                ),
                500,
            )
    else:
        return jsonify(
            {
                "success": False,
                "message": "Failed to create item. Please refer to the log for details.",
            },
            500,
        )


@ADMIN_API_ROUTES.route("/items/<item_id>", methods=["DELETE"])
def delete_item(item_id):
    """
    删除指定 ID 的物品数据
    """
    # 云函数兼容性处理：获取 NotionItemTrackerClient 实例
    try:
        client: Client = current_app.client
        result = client.delete(item_id)
    except Exception as e:
        return jsonify(
            {
                "success": False,
                "message": "Failed to delete item. Please refer to the log for details.",
                "error": str(e),
            }
        )
    if result:
        return jsonify(
            {
                "success": True,
                "message": "Item deleted successfully.",
            }
        )
    else:
        return (
            jsonify(
                {
                    "success": False,
                    "message": "Failed to delete item. Please refer to the log for details.",
                }
            ),
            500,
        )


@ADMIN_API_ROUTES.route("/items/<item_id>", methods=["PATCH"])
def modify_item(item_id: str):
    """
    修改特定物品数据
    """
    client: Client = current_app.client
    data = request.json
    name = data.get("name", "")
    entry_date = data.get("entry_date")
    purchase_price = data.get("purchase_price")
    additional_value = data.get("additional_value")
    retirement_date = data.get("retirement_date")
    remark = data.get("remark", "")
    if SCRIPT_PATTERN.search(name) or SCRIPT_PATTERN.search(remark):
        return jsonify(
            {
                "success": False,
                "message": "Invalid input detected. No script tags allowed.",
            }
        ), 400
    try:
        result = client.edit(
            item_id,
            name=name,
            purchase_price=float(purchase_price),
            additional_price=(
                float(additional_value) if additional_value is not None else 0.0
            ),
            entry_date=entry_date,
            retire_date=retirement_date if retirement_date is not None else None,
            remark=remark if remark is not None else "",
        )
    except Exception as e:
        return jsonify(
            {
                "success": False,
                "message": "Failed to update item. Please refer to the log for details.",
                "error": str(e),
            }
        )

    if result:
        return jsonify(
            {
                "success": True,
                "message": "Item updated successfully.",
            }
        )
    else:
        return (
            jsonify(
                {
                    "success": False,
                    "message": "Failed to update item. Please refer to the log for details.",
                }
            ),
            500,
        )

@PUBLIC_API_ROUTES.route("/trigger", methods=["GET"])
def trigger_bot():
    """
    触发机器人访问
    """
    try:
        trigger_bot_access()
        return jsonify({"success": True, "message": "Bot access triggered successfully"}), 200
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500
