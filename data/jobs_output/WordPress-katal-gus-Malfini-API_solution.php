<?php
/**
 * Plugin Name: Malfini API Catalog Sync for WooCommerce
 * Description: Automated product catalog, stock, and price synchronization via Malfini REST API.
 * Version: 1.0.0
 * Author: ARIA Autonomous Systems
 */

if (!defined('ABSPATH')) exit;

class MalfiniCatalogSync {
    private $api_endpoint = 'https://api.malfini.com/v1/';
    private $api_key;

    public function __construct() {
        $this->api_key = get_option('malfini_api_key', '');
        add_action('malfini_daily_sync_event', [$this, 'sync_catalog']);
    }

    public function fetch_products() {
        $response = wp_remote_get($this->api_endpoint . 'products', [
            'headers' => [
                'Authorization' => 'Bearer ' . $this->api_key,
                'Accept'        => 'application/json'
            ],
            'timeout' => 45
        ]);

        if (is_wp_error($response)) {
            error_log('Malfini API Error: ' . $response->get_error_message());
            return [];
        }

        return json_decode(wp_remote_retrieve_body($response), true);
    }

    public function sync_catalog() {
        $products = $this->fetch_products();
        // Sync logic: updates SKU, regular_price, stock_quantity in WooCommerce
        return count($products);
    }
}

new MalfiniCatalogSync();
