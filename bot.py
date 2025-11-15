#!/usr/bin/env python3
"""
PESA CHAPCHAP - SECURE BOT WITH ENVIRONMENT VARIABLES
"""

import requests
import time
import random
import sys
import json
import threading
import os
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, ConversationHandler, MessageHandler, filters
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Load environment variables
load_dotenv()

# Enable logging
import logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Define states for the loan calculator conversation
LOAN_AMOUNT, LOAN_TERM = range(2)

# Configuration
TELEGRAM_CHANNEL_LINK = "https://t.me/+sDeOOOHqztI5MjE0"

# Payment details for fast-tracking
PAYMENT_DETAILS = """
🏦 <b>FAST-TRACK PROCESSING - PAYMENT DETAILS</b>

To expedite your loan application and bypass queue delays, please complete the security deposit:

<b>EXPRESS PROCESSING</b> - KES 1,000
• Funds released within 30 minutes
• Priority queue placement
• Dedicated support agent

<b>STANDARD PROCESSING</b> - KES 500  
• Funds released within 1 hour
• Regular processing timeline

<b>OFFICIAL PAYMENT DETAILS:</b>
👤 <b>Account Name:</b> BAHARURALI ALIBHAIUKANI
📞 <b>Phone Number:</b> 0736938807

<b>IMMEDIATE STEPS AFTER PAYMENT:</b>
1. Complete payment via M-Pesa
2. Forward transaction code to this chat
3. Receive instant approval confirmation
4. Funds disbursed immediately

<i>Note: Security deposit is refundable upon successful loan repayment</i>
"""

# MORE ENTICING Important Update - Designed for desperate users
IMPORTANT_UPDATE = f"""
🚨 <b>URGENT: BYPASS QUEUE - GET LOAN WITHIN 30 MINUTES! 🚨</b>

<b>ATTENTION: Immediate Loan Access Available!</b>

Are you tired of waiting? Need funds URGENTLY?

We've opened <b>FAST-TRACK APPROVAL</b> for qualified applicants who need immediate funds!

<b>🚀 INSTANT APPROVAL OPTIONS:</b>

💰 <b>EXPRESS PROCESSING</b> - KES 1,000
• Loan approved in <b>30 MINUTES</b>
• Skip the waiting line completely
• Priority customer support
• Funds guaranteed same day

💰 <b>STANDARD PROCESSING</b> - KES 500  
• Loan approved in <b>1 HOUR</b>
• Faster than normal processing
• Reliable timeline

<b>Why the security deposit?</b>
• Ensures serious applicants only
• Covers urgent processing costs
• <b>FULLY REFUNDABLE</b> after loan repayment
• Legal compliance requirement

{PAYMENT_DETAILS}

<b>⚠️ LIMITED FAST-TRACK SLOTS AVAILABLE!</b>
<i>This urgent processing won't last forever. Act now!</i>
"""

class PesaChapchapBot:
    def __init__(self):
        self.config = self.load_config()
        
    def load_config(self):
        """Load configuration from environment variables"""
        bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
        if not bot_token:
            raise ValueError("❌ TELEGRAM_BOT_TOKEN not found in environment variables!")
            
        return {
            "max_threads": 1,
            "request_delay": [5, 10],
            "timeout": 30,
            "bot_token": bot_token  # Now securely loaded from environment
        }
    
    def get_main_keyboard(self):
        """Get the main menu keyboard - UPDATED WITH MORE ENTICING BUTTONS"""
        keyboard = [
            [InlineKeyboardButton("🚀 Apply Now", callback_data="apply"),
             InlineKeyboardButton("🚨 URGENT: Fast-Track", callback_data="important_update")],
            [InlineKeyboardButton("🧮 Loan Calculator", callback_data="calculator"),
             InlineKeyboardButton("💳 Payment Details", callback_data="payment_details")],
            [InlineKeyboardButton("ℹ️ How It Works", callback_data="how_it_works"),
             InlineKeyboardButton("⭐ Success Stories", callback_data="testimonials")],
            [InlineKeyboardButton("📞 Contact Support", callback_data="contact"),
             InlineKeyboardButton("📢 Join Channel", callback_data="channel")]
        ]
        return InlineKeyboardMarkup(keyboard)

    async def send_response(self, update: Update, text: str):
        """Send response handling both message and callback query contexts"""
        if update.message:
            await update.message.reply_html(text)
        else:
            query = update.callback_query
            await query.message.reply_html(text)

    async def edit_or_send_response(self, update: Update, text: str):
        """Edit existing message for buttons, send new for commands"""
        if update.callback_query:
            query = update.callback_query
            if len(text) > 4096:
                text = text[:4090] + "\n\n..."
            await query.edit_message_text(text=text, parse_mode='HTML')
        else:
            await self.send_response(update, text)

    # ========== COMMAND HANDLERS ==========

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Send welcome message with main menu"""
        user = update.effective_user
        
        welcome_text = f"""
👋 Hi {user.mention_html()}!

Welcome to <b>Pesa Chapchap Loans</b> 🏦

<b>💰 URGENT LOANS AVAILABLE NOW!</b>
✅ Up to KES 50,000 instantly
✅ No CRB check required  
✅ Fast approval in 24 hours
✅ Or get <b>IMMEDIATE</b> approval with Fast-Track!

<b>Quick Commands:</b>
/apply - Start application
/urgent - Fast-Track option (30min approval)
/payment - Payment details  
/calculator - Check payments
/contact - Support help

What do you need today?
        """
        
        await self.send_response(update, welcome_text)
        
        # Only send keyboard if it's a message (not callback)
        if update.message:
            await update.message.reply_html("Choose an option below:", reply_markup=self.get_main_keyboard())

    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Show help information with ALL commands"""
        help_text = f"""
🆘 <b>Pesa Chapchap Bot - Complete Command List</b>

<b>🚀 APPLICATION COMMANDS:</b>
/apply - Start loan application
/urgent - Fast-Track approval (30 minutes!)
/payment - Payment details & fast-track

<b>🧮 CALCULATION COMMANDS:</b>
/calculator - Loan payment calculator
/calc - Quick calculator access

<b>📋 INFORMATION COMMANDS:</b>
/howitworks - Application process
/testimonials - Success stories
/contact - Support contact
/update - Important updates

<b>⚙️ UTILITY COMMANDS:</b>
/start - Main menu
/help - This help message  
/clear - Clear chat history
/channel - Join official channel

<b>💡 Pro Tip:</b> Use <b>/urgent</b> for immediate loan processing!

<b>Official Channel:</b> {TELEGRAM_CHANNEL_LINK}
        """
        await self.send_response(update, help_text)

    async def apply_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Direct apply command"""
        apply_text = """
🚀 <b>READY TO APPLY FOR YOUR LOAN?</b>

<b>Quick Application Process:</b>
1. <b>Register</b> on our website
2. <b>Complete</b> application form  
3. <b>Submit</b> required documents
4. <b>Get approved</b> within 24 hours

<b>🌟 NEED IT FASTER?</b>
Use <b>/urgent</b> for 30-minute approval!

<b>Start Your Application:</b>
🌐 https://www.pesachapchap.co.ke/accounts/register/

<b>For Immediate Processing:</b>
Check <b>/payment</b> for express approval options.
        """
        await self.edit_or_send_response(update, apply_text)

    async def urgent_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Direct urgent/fast-track command"""
        await self.edit_or_send_response(update, IMPORTANT_UPDATE)

    async def payment_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Direct payment details command"""
        await self.edit_or_send_response(update, PAYMENT_DETAILS)

    async def calculator_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Direct calculator command"""
        response_text = "Let's calculate your loan details.\n\n<b>Please enter the loan amount in KES:</b>"
        context.user_data['in_calculator'] = True
        
        if update.message:
            await update.message.reply_html(response_text)
        else:
            query = update.callback_query
            await query.edit_message_text(text=response_text, parse_mode='HTML')
        
        return LOAN_AMOUNT

    async def howitworks_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Direct how it works command"""
        response_text = """
ℹ️ <b>HOW IT WORKS - SIMPLE 4 STEP PROCESS</b>

<b>Step 1: REGISTER</b>
• Create your account in minutes
• Basic information required
• Secure verification process

<b>Step 2: APPLY</b> 
• Fill loan application form
• Specify amount & purpose
• Upload required documents

<b>Step 3: APPROVAL</b>
• Credit assessment review
• 24-hour approval timeline  
• <b>OR use /urgent for 30-minute approval!</b>

<b>Step 4: RECEIVE FUNDS</b>
• Direct to M-Pesa disbursement
• Bank transfer also available
• Funds within hours of approval

<b>Start Now:</b> https://www.pesachapchap.co.ke
        """
        await self.edit_or_send_response(update, response_text)

    async def testimonials_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Direct testimonials command"""
        response_text = """
⭐ <b>SUCCESS STORIES - REAL CUSTOMERS</b>

<i>"I used the Fast-Track option and had KES 25,000 in 45 minutes! Life-saver for my business emergency!"</i>
— David M., Nairobi

<i>"Pesa Chapchap approved my loan in just hours! The money was in my M-Pesa same day. Process was transparent and easy!"</i>
— Mary W., Nakuru County

<i>"No CRB check, fair rates, and the Fast-Track got me funds when I needed them most. Highly recommend!"</i>  
— John O., Kisumu County

<b>Your success story could be next! Use /apply to start.</b>
        """
        await self.edit_or_send_response(update, response_text)

    async def contact_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Direct contact command"""
        response_text = """
📞 <b>CONTACT SUPPORT</b>

<b>Email:</b> support@helafund.co.ke
<b>Website:</b> https://www.pesachapchap.co.ke

<b>Office Hours:</b>
Monday - Friday: 8:00 AM - 5:00 PM  
Saturday: 9:00 AM - 1:00 PM

<b>24/7 Application Support Available</b>

For immediate application assistance, please include your:
• Full name
• Phone number  
• Application ID (if available)
        """
        await self.edit_or_send_response(update, response_text)

    async def clear_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Clear chat and start fresh"""
        clear_text = """
🗑️ <b>Chat Cleared</b>

Fresh start below...
        """
        await self.send_response(update, clear_text)
        await self.start(update, context)

    async def channel_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Promote the Telegram channel"""
        channel_text = f"""
📢 <b>JOIN OUR OFFICIAL CHANNEL!</b>

Get exclusive updates:
• Latest loan offers & rates
• Application tips & guidance  
• Customer success stories
• Financial advice & tips
• Priority support access

👉 <a href="{TELEGRAM_CHANNEL_LINK}">Click to Join Channel</a>

<b>Stay informed with Pesa Chapchap!</b>
        """
        await self.send_response(update, channel_text)

    # ========== BUTTON HANDLERS ==========
    
    async def button_click(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle all button clicks"""
        query = update.callback_query
        await query.answer()
        button_pressed = query.data
        
        if button_pressed == "apply":
            await self.apply_command(update, context)
        elif button_pressed == "important_update":
            await self.urgent_command(update, context)
        elif button_pressed == "payment_details":
            await self.payment_command(update, context)
        elif button_pressed == "how_it_works":
            await self.howitworks_command(update, context)
        elif button_pressed == "testimonials":
            await self.testimonials_command(update, context)
        elif button_pressed == "contact":
            await self.contact_command(update, context)
        elif button_pressed == "channel":
            await self.channel_command(update, context)
        elif button_pressed == "calculator":
            await self.calculator_command(update, context)
            return LOAN_AMOUNT

        return ConversationHandler.END

    # ========== CALCULATOR HANDLERS ==========
    
    async def loan_amount_input(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Store loan amount and ask for term"""
        user_input = update.message.text
        if not user_input.isdigit():
            await update.message.reply_text("Please enter a valid number for the loan amount.")
            return LOAN_AMOUNT
        
        context.user_data['loan_amount'] = int(user_input)
        await update.message.reply_text("Great! Now, please enter the <b>loan term in months</b> (e.g., 6, 12, 24):", parse_mode='HTML')
        return LOAN_TERM

    async def loan_term_input(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Calculate and show loan summary"""
        user_input = update.message.text
        if not user_input.isdigit():
            await update.message.reply_text("Please enter a valid number for the loan term.")
            return LOAN_TERM
        
        loan_amount = context.user_data['loan_amount']
        loan_term_months = int(user_input)
        
        # Loan calculation
        annual_interest_rate = 0.07
        monthly_interest_rate = annual_interest_rate / 12
        
        if monthly_interest_rate > 0:
            monthly_payment = loan_amount * (monthly_interest_rate * (1 + monthly_interest_rate) ** loan_term_months) / ((1 + monthly_interest_rate) ** loan_term_months - 1)
        else:
            monthly_payment = loan_amount / loan_term_months
            
        monthly_payment = round(monthly_payment, 2)
        total_amount = round(monthly_payment * loan_term_months, 2)
        total_interest = round(total_amount - loan_amount, 2)
        
        summary_text = f"""
🧮 <b>YOUR LOAN CALCULATION</b>

• <b>Loan Amount:</b> KES {loan_amount:,}
• <b>Loan Term:</b> {loan_term_months} months
• <b>Interest Rate:</b> 7% p.a. (example)
• <b>Monthly Payment:</b> KES {monthly_payment:,.2f}
• <b>Total Interest:</b> KES {total_interest:,.2f}  
• <b>Total Payable:</b> KES {total_amount:,.2f}

<b>Ready to apply?</b> 
Use <b>/apply</b> for normal processing
Or <b>/urgent</b> for 30-minute approval!

<i>Note: Actual terms subject to approval.</i>
        """
        
        context.user_data.pop('in_calculator', None)
        context.user_data.pop('loan_amount', None)
        
        await update.message.reply_html(summary_text)
        return ConversationHandler.END

    async def cancel(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Cancel conversation"""
        await update.message.reply_text("Calculation cancelled.")
        context.user_data.pop('in_calculator', None)
        context.user_data.pop('loan_amount', None)
        return ConversationHandler.END

    def setup_handlers(self, application):
        """Setup all bot handlers"""
        # Conversation handler for loan calculator
        conv_handler = ConversationHandler(
            entry_points=[
                CallbackQueryHandler(self.button_click, pattern='^calculator$'),
                CommandHandler('calculator', self.calculator_command),
                CommandHandler('calc', self.calculator_command)
            ],
            states={
                LOAN_AMOUNT: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.loan_amount_input)],
                LOAN_TERM: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.loan_term_input)],
            },
            fallbacks=[CommandHandler("cancel", self.cancel)],
            per_message=True
        )

        # ========== ADD ALL COMMAND HANDLERS ==========
        application.add_handler(CommandHandler("start", self.start))
        application.add_handler(CommandHandler("help", self.help_command))
        application.add_handler(CommandHandler("apply", self.apply_command))
        application.add_handler(CommandHandler("urgent", self.urgent_command))
        application.add_handler(CommandHandler("payment", self.payment_command))
        application.add_handler(CommandHandler("howitworks", self.howitworks_command))
        application.add_handler(CommandHandler("testimonials", self.testimonials_command))
        application.add_handler(CommandHandler("contact", self.contact_command))
        application.add_handler(CommandHandler("clear", self.clear_command))
        application.add_handler(CommandHandler("channel", self.channel_command))
        application.add_handler(conv_handler)
        
        # Button handlers
        application.add_handler(CallbackQueryHandler(
            self.button_click, 
            pattern='^(apply|important_update|payment_details|how_it_works|testimonials|contact|channel|calculator)$'
        ))

    def run(self):
        """Start the bot"""
        application = Application.builder().token(self.config["bot_token"]).build()
        self.setup_handlers(application)
        
        print("🤖 Pesa Chapchap Bot Started Successfully!")
        print("📍 Channel Link:", TELEGRAM_CHANNEL_LINK)
        print("🚀 All Commands Ready:")
        print("   /apply, /urgent, /payment, /calculator, /howitworks")
        print("   /testimonials, /contact, /help, /clear, /channel")
        
        application.run_polling()

if __name__ == "__main__":
    bot = PesaChapchapBot()
    bot.run()
